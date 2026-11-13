import model from './flood-model.json' with { type: 'json' };
import { weather, coordinates, HttpError } from './services.mjs';
export function predictProbability(input) {
  const values = model.features.map(name => Math.fround(Number(input[name])));
  const rf = model.rf.reduce((sum, tree) => {
    let i = 0;
    while (tree.left[i] !== -1) i = values[tree.feature[i]] <= tree.threshold[i] ? tree.left[i] : tree.right[i];
    return sum + tree.values[i];
  }, 0) / model.rf.length;
  function leaf(node) {
    if ('leaf' in node) return node.leaf;
    const index = model.features.indexOf(node.split);
    const value = values[index];
    const next = Number.isNaN(value) ? node.missing : value < node.split_condition ? node.yes : node.no;
    return leaf(node.children.find(c => c.nodeid === next));
  }
  const margin = Math.log(model.base_score / (1 - model.base_score)) + model.xgb.reduce((sum, tree) => sum + leaf(tree), 0);
  return 0.65 / (1 + Math.exp(-margin)) + 0.35 * rf;
}
const defaults = { rainfall_current_mm: 15, rainfall_24h_mm: 65, rainfall_7d_mm: 180, rainfall_forecast_24h_mm: 40, temperature_c: 28, humidity_pct: 85, wind_speed_kmh: 24, elevation_m: 25, slope_deg: 2.5, distance_to_water_km: 1.2, historical_flood_freq: 0.6, population_density_sqkm: 3200, soil_moisture_index: 0.78, river_water_level_m: 13.5 };
export async function assessRisk(input) {
  const position = coordinates(input);
  const live = await weather(position);
  const hourly = live.hourly;
  const historical = live.historical_hourly;
  const now = live.current.timestamp;
  const recent = historical.time.map((time, i) => ({ time, rain: historical.precipitation[i] })).filter(p => p.time <= now);
  const future = hourly.time.map((time, i) => ({ time, rain: hourly.precipitation[i] })).filter(p => p.time > now);
  const observed = { rainfall_current_mm: live.current.rainfall, rainfall_24h_mm: recent.slice(-24).reduce((s,p) => s + p.rain, 0), rainfall_7d_mm: recent.slice(-168).reduce((s,p) => s + p.rain, 0), rainfall_forecast_24h_mm: future.slice(0,24).reduce((s,p) => s + p.rain, 0), temperature_c: live.current.temperature, humidity_pct: live.current.humidity, wind_speed_kmh: live.current.wind_speed, elevation_m: live.current.elevation_m };
  const features = { ...defaults, ...observed };
  const estimated_inputs = model.features.filter(name => !(name in observed) && !(name in input));
  for (const name of model.features) {
    if (input[name] !== undefined && input[name] !== '') {
      if (!Number.isFinite(Number(input[name]))) throw new HttpError(400, `Invalid numeric feature: ${name}`);
      features[name] = Number(input[name]);
    }
  }
  const score = +(predictProbability(features) * 100).toFixed(1);
  const level = score <= 30 ? 'LOW' : score <= 60 ? 'MODERATE' : score <= 80 ? 'HIGH' : 'CRITICAL';
  const action = 'Experimental flood estimate using the repository’s trained models. Some hydrological inputs are assumed. Check official IMD/OSDMA advisories and follow local evacuation orders.';
  const prediction = { ...features, ...position, location_name: String(input.location_name || input.catchment_location || 'Selected location').slice(0,200), risk_score: score, risk_level: level, confidence: null, model_mode: 'EXPERIMENTAL_XGBOOST_RF_ENSEMBLE', recommended_action: action, estimated_inputs, features, is_demo: false, created_at: new Date().toISOString() };
  return { success: true, prediction, explanation: { ...prediction, contributing_factors: model.features.map(name => ({ factor: name.replaceAll('_', ' '), value: features[name], contribution: estimated_inputs.includes(name) ? 'ASSUMED' : 'INPUT', description: estimated_inputs.includes(name) ? 'Default assumption; no live observation available.' : name in input ? 'User supplied value' : 'Open-Meteo weather data' })) }, risk_score: score, risk_percentage: score, risk_level: level, risk_type: 'FLOOD', flood_risk_pct: score, cyclone_risk_pct: null, model_mode: prediction.model_mode, recommended_action: action, weather_telemetry: observed, forecast_7d: live.daily.time.map((date,i) => ({ date, rain_mm: live.daily.precipitation_sum[i], temp_max: live.daily.temperature_2m_max[i], temp_min: live.daily.temperature_2m_min[i] })) };
}
