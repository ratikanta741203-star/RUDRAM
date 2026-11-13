export class HttpError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}
export function coordinates(input) {
  const rawLat = input.latitude ?? input.lat;
  const rawLon = input.longitude ?? input.lon ?? input.lng;
  if (rawLat === undefined || rawLon === undefined || rawLat === '' || rawLon === '') throw new HttpError(400, 'Latitude and longitude are required.');
  const latitude = Number(rawLat), longitude = Number(rawLon);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude) || Math.abs(latitude) > 90 || Math.abs(longitude) > 180) throw new HttpError(400, 'Invalid coordinates.');
  return { latitude, longitude };
}
export async function fetchJson(url, options = {}) {
  try {
    const response = await fetch(url, { ...options, signal: AbortSignal.timeout(10000) });
    if (!response.ok) throw new Error('upstream');
    return await response.json();
  } catch { throw new HttpError(503, 'The live data provider is temporarily unavailable. Please try again.'); }
}
export async function weather(input) {
  const { latitude, longitude } = coordinates(input);
  const params = new URLSearchParams({ latitude, longitude, current: 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_gusts_10m', hourly: 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m', daily: 'temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code', timezone: 'auto', past_days: '7', forecast_days: String(Math.min(7, Math.max(1, Number(input.forecast_days) || 7))) });
  const data = await fetchJson(`https://api.open-meteo.com/v1/forecast?${params}`);
  const c = data.current;
  if (!c) throw new HttpError(503, 'Current weather is unavailable.');
  const conditions = c.weather_code === 0 ? 'Clear sky' : c.weather_code < 4 ? 'Cloudy' : c.weather_code >= 95 ? 'Thunderstorm' : ((c.weather_code >= 71 && c.weather_code <= 77) || c.weather_code === 85 || c.weather_code === 86) ? 'Snow' : c.weather_code >= 51 ? 'Rain' : 'Fog';
  const sliceSeries = (series, indices) => Object.fromEntries(Object.entries(series || {}).map(([key, values]) => [key, indices.map(i => values[i])]));
  const currentDate = c.time.slice(0,10);
  const futureIndices = data.hourly.time.flatMap((time,i) => time >= c.time ? [i] : []);
  const pastIndices = data.hourly.time.flatMap((time,i) => time < c.time ? [i] : []);
  const futureHourly = sliceSeries(data.hourly, futureIndices);
  const historicalHourly = sliceSeries(data.hourly, pastIndices);
  const daily = sliceSeries(data.daily, data.daily.time.flatMap((date,i) => date >= currentDate ? [i] : []));
  const rainfall24h = historicalHourly.precipitation.slice(-24).reduce((sum,rain) => sum + Number(rain || 0),0);
  return { success: true, source: 'Open-Meteo', is_live: true, latitude, longitude, timezone: data.timezone,
    current: { temperature: c.temperature_2m, humidity: c.relative_humidity_2m, rainfall: c.precipitation, rainfall_24h: +rainfall24h.toFixed(2), wind_speed: c.wind_speed_10m, wind_gust: c.wind_gusts_10m, weather_code: c.weather_code, condition: conditions, elevation_m: data.elevation, timestamp: c.time },
    historical_hourly: historicalHourly, hourly: { ...futureHourly, temperature: futureHourly.temperature_2m, rainfall: futureHourly.precipitation, humidity: futureHourly.relative_humidity_2m, wind_speed: futureHourly.wind_speed_10m }, daily, updated_at: new Date().toISOString() };
}
export async function geocode(input) {
  if (input.lat !== undefined || input.latitude !== undefined || /^-?\d+(\.\d+)?,\s*-?\d+(\.\d+)?$/.test(input.q || '')) {
    const q = /^-?\d+(\.\d+)?,\s*-?\d+(\.\d+)?$/.test(input.q || '') ? input.q.split(',') : null;
    const { latitude, longitude } = coordinates(q ? { lat: q[0], lon: q[1] } : input);
    const params = new URLSearchParams({ lat: latitude, lon: longitude, format: 'jsonv2' });
    const data = await fetchJson(`https://nominatim.openstreetmap.org/reverse?${params}`, { headers: { 'User-Agent': 'RUDRAM/2.0 disaster management' } });
    const item = { ...data, lat: latitude, lon: longitude, latitude, longitude, place_name: data.display_name, name: data.name || data.display_name };
    return { success: true, ...item, results: [item] };
  }
  const query = String(input.q || input.address || input.query || '').trim();
  if (query.length < 2 || query.length > 200) throw new HttpError(400, 'Enter a location between 2 and 200 characters.');
  let results;
  if (input.address) {
    const matches = await fetchJson(`https://nominatim.openstreetmap.org/search?${new URLSearchParams({ q: [query,input.postal_code].filter(Boolean).join(' '), format: 'jsonv2', addressdetails: '1', limit: '5' })}`, { headers: { 'User-Agent': 'RUDRAM/2.0 disaster management' } });
    results = matches.map(p => ({ name: p.name || p.display_name, place_name: p.name || p.display_name, display_name: p.display_name, latitude: Number(p.lat), longitude: Number(p.lon), postal_code: p.address?.postcode || '' }));
  } else {
    const data = await fetchJson(`https://geocoding-api.open-meteo.com/v1/search?${new URLSearchParams({ name: query, count: '10', language: 'en', format: 'json' })}`);
    results = (data.results || []).map(p => ({ ...p, display_name: [p.name, p.admin1, p.country].filter(Boolean).join(', '), place_name: p.name, elevation_m: p.elevation }));
  }
  if (results.length && input.address) {
    try {
      const elevations = await fetchJson(`https://api.open-meteo.com/v1/elevation?${new URLSearchParams({ latitude: results.map(p => p.latitude).join(','), longitude: results.map(p => p.longitude).join(',') })}`);
      results.forEach((p,i) => { p.elevation_m = elevations.elevation[i]; });
    } catch { results.forEach(p => { p.elevation_m = null; }); }
  }
  results = results.map(p => ({ ...p, lat: p.latitude, lon: p.longitude }));
  return { ...(results[0] || {}), success: true, multiple: results.length > 1, results };

}
export function distance(a, b) {
  const rad = n => Number(n) * Math.PI / 180;
  const dlat = rad(b.latitude - a.latitude), dlon = rad(b.longitude - a.longitude);
  return 6371 * 2 * Math.asin(Math.sqrt(Math.sin(dlat / 2) ** 2 + Math.cos(rad(a.latitude)) * Math.cos(rad(b.latitude)) * Math.sin(dlon / 2) ** 2));
}
export async function roadRoute(input) {
  const start = coordinates({ latitude: input.start_lat ?? input.origin_lat ?? input.latitude, longitude: input.start_lon ?? input.origin_lon ?? input.longitude });
  const end = coordinates({ latitude: input.end_lat ?? input.destination_lat, longitude: input.end_lon ?? input.destination_lon });
  const url = `https://router.project-osrm.org/route/v1/driving/${start.longitude},${start.latitude};${end.longitude},${end.latitude}?overview=full&geometries=geojson&alternatives=true&steps=true`;
  const data = await fetchJson(url);
  if (data.code !== 'Ok' || !data.routes?.length) throw new HttpError(404, 'No road route was found between these locations.');
  return { success: true, result: { source: 'OSRM / OpenStreetMap', safety_notice: 'Road directions only. Flood conditions and road closures are not verified. Follow local evacuation orders.', routes: data.routes.map(r => ({ distance_km: +(r.distance / 1000).toFixed(2), duration_minutes: +(r.duration / 60).toFixed(1), coordinates: r.geometry.coordinates.map(([lon, lat]) => [lat, lon]), geometry: r.geometry, steps: r.legs.flatMap(l => l.steps) })) } };
}
