import express from 'express';
import { render, routes } from './render.mjs';
import locations from './locations.json' with { type: 'json' };
import knowledge from './knowledge.json' with { type: 'json' };
import { HttpError, weather, geocode, roadRoute, coordinates, distance, fetchJson } from './services.mjs';
import { assessRisk } from './risk.mjs';

const pages = {
  '/': ['dashboard/index.html', 'dashboard'], '/dashboard/': ['dashboard/index.html', 'dashboard'],
  '/map/': ['map/index.html', 'map'], '/disasters/': ['disasters/list.html', 'disasters_list'],
  '/risk/': ['risk/predict.html', 'risk_prediction'], '/population/': ['population/exposure.html', 'population'],
  '/alerts/': ['alerts/index.html', 'alerts'], '/evacuation/': ['evacuation/index.html', 'evacuation'],
  '/shelters/': ['shelters/index.html', 'shelters'], '/resources/': ['resources/index.html', 'resources'],
  '/assistant/': ['assistant/chat.html', 'assistant'], '/satellite/': ['satellite/index.html', 'satellite'],
  '/reports/': ['reports/index.html', 'reports'], '/settings/': ['settings/index.html', 'settings'],
  '/login/': ['accounts/login.html', 'login'], '/citizen/signup/': ['accounts/signup.html', 'citizen_signup'],
  '/admin-dashboard/': ['admin/dashboard.html', 'admin_dashboard'], '/operator-dashboard/': ['operator/dashboard.html', 'operator_dashboard'],
  '/drone-view/': ['disasters/drone.html', 'drone_view'],
};
const collections = ['shelters', 'resources', 'rescue-teams', 'alerts', 'disasters', 'risk-zones', 'population', 'infrastructure', 'rivers', 'dams', 'predictions', 'approval-requests', 'audit-logs'];
const protectedPages = new Set(['admin_dashboard', 'operator_dashboard', 'settings', 'reports', 'drone_view']);
const jsonForScript = value => JSON.stringify(value).replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');
const listResult = (res, rows) => res.json({ success: true, count: rows.length, next: null, previous: null, results: rows });
const decorateShelter = s => ({ ...s, available_capacity: Math.max(0, Number(s.total_capacity) - Number(s.current_occupancy || 0)), occupancy_percentage: s.total_capacity ? +(Number(s.current_occupancy || 0) / s.total_capacity * 100).toFixed(1) : 0 });
function validateRecord(kind, input) {
  const data = Object.fromEntries(Object.entries(input).filter(([key]) => !['id', 'created_at', 'updated_at', 'csrfmiddlewaretoken'].includes(key)));
  for (const [key, value] of Object.entries(data)) {
    if (typeof value === 'string' && value.length > 5000) throw new HttpError(400, 'A field is too long.');
    if (/^(latitude|longitude|total_capacity|current_occupancy|quantity|quantity_available|quantity_allocated|quantity_required|stock_quantity|members_count|team_size|elevation_m)$/.test(key)) {
      data[key] = Number(value);
      if (!Number.isFinite(data[key])) throw new HttpError(400, `Invalid ${key}.`);
    }
  }
  if (data.latitude !== undefined || data.longitude !== undefined) coordinates(data);
  if (kind === 'shelters') {
    if (!String(data.name || '').trim()) throw new HttpError(400, 'Shelter name is required.');
    if (!Number.isInteger(data.total_capacity) || data.total_capacity < 0 || !Number.isInteger(Number(data.current_occupancy || 0)) || Number(data.current_occupancy || 0) < 0 || Number(data.current_occupancy || 0) > data.total_capacity) throw new HttpError(400, 'Occupancy must be between zero and the shelter capacity.');
    data.current_occupancy = Number(data.current_occupancy || 0);
    data.status ||= 'OPEN';
  }
  for (const key of ['quantity_available','quantity_allocated','quantity_required','members_count']) {
    if (data[key] !== undefined && (!Number.isInteger(data[key]) || data[key] < 0)) throw new HttpError(400, `Invalid ${key}.`);
  }
  if (kind === 'alerts') {
    if (!String(data.title || '').trim()) throw new HttpError(400, 'Alert title is required.');
    if (!['INFO', 'WARNING', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL'].includes(data.severity)) throw new HttpError(400, 'Invalid alert severity.');
    data.is_active = data.is_active !== false;
    data.broadcast_channels = 'Website';
  }
  data.is_demo = false;
  return data;
}
export function createApp(repository, { fetchWeather = weather, searchLocation = geocode, route = roadRoute, assess = assessRisk, authenticate } = {}) {
  const app = express();
  app.disable('x-powered-by');
  app.set('trust proxy', 1);
  app.use(express.json({ limit: '32kb' }));
  app.use(express.urlencoded({ extended: false, limit: '32kb' }));
  app.use('/static', express.static(new URL('../static/', import.meta.url).pathname));
  app.use(async (req, res, next) => {
    if (!['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
      const origin = req.get('origin');
      if (req.get('sec-fetch-site') === 'cross-site' || (origin && origin !== `${req.protocol}://${req.get('host')}` && origin !== process.env.URL && origin !== process.env.DEPLOY_PRIME_URL)) return next(new HttpError(403, 'Cross-site requests are not allowed.'));
    }
    req.identity = null;
    try {
      if (authenticate) req.identity = await authenticate(req);
      else {
        const cookie = req.headers.cookie?.split(';').map(c => c.trim()).find(c => c.startsWith('nf_jwt='));
        const bearer = req.get('authorization')?.match(/^Bearer (.+)$/)?.[1];
        const token = bearer || (cookie ? decodeURIComponent(cookie.slice(7)) : null);
        if (token && process.env.URL) {
          const response = await fetch(`${process.env.URL.replace(/\/$/, '')}/.netlify/identity/user`, { headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(4000) });
          if (response.ok) req.identity = await response.json();
        }
      }
    } catch { /* Failed verification remains anonymous. */ }
    const roles = req.identity?.app_metadata?.roles || req.identity?.roles || [];
    req.role = roles.includes('ADMIN') || roles.includes('admin') ? 'ADMIN' : roles.includes('EMERGENCY_OPERATOR') ? 'EMERGENCY_OPERATOR' : 'CITIZEN';
    next();
  });
  const requireStaff = (req, res, next) => {
    if (!req.identity) return next(new HttpError(401, 'Sign in to perform this action.'));
    if (!['ADMIN', 'EMERGENCY_OPERATOR'].includes(req.role)) return next(new HttpError(403, 'An administrator or emergency operator role is required.'));
    next();
  };
  const requireAdmin = (req, res, next) => req.role === 'ADMIN' ? next() : next(new HttpError(req.identity ? 403 : 401, 'Administrator access is required.'));
  app.get('/api/current-user/', (req, res) => res.json({ authenticated: !!req.identity, is_authenticated: !!req.identity, role: req.role, user: req.identity ? { id: req.identity.id, email: req.identity.email, role: req.role } : null }));
  app.get('/api/health/', async (req, res) => {
    try { await repository.healthy(); res.json({ status: 'healthy', application: 'RUDRAM', runtime: 'Netlify Server', database: 'connected', database_engine: 'Netlify Database / PostgreSQL', demo_mode: false }); }
    catch { res.status(503).json({ status: 'degraded', application: 'RUDRAM', runtime: 'Netlify Server', database: 'unavailable', detail: 'The database is not available yet. Please retry shortly.' }); }
  });
  app.get(['/api/data-sources/', '/api/data-sources/status/'], (req, res) => res.json({ success: true, sources: [{ source_name: 'open_meteo', display_name: 'Open-Meteo', status: 'ON_DEMAND', is_live: true }, { source_name: 'osrm', display_name: 'OSRM road routing', status: 'ON_DEMAND', is_live: true }, { source_name: 'satellite', display_name: 'Satellite analysis', status: 'UNAVAILABLE', is_live: false }], note: 'Live provider availability is checked when requested.' }));
  app.get('/api/locations/states/', (req, res) => res.json({ success: true, states: locations.INDIAN_STATES_DATA }));
  app.get('/api/locations/india-hubs/', (req, res) => res.json({ success: true, hubs: locations.INDIAN_STATES_DATA.map(s => ({ city: s.capital, state: s.name, lat: s.lat, lon: s.lon })) }));
  app.get('/api/locations/high-alerts/', async (req, res) => res.json({ success: true, alerts: (await repository.list('alerts')).filter(a => a.is_active && ['HIGH', 'CRITICAL'].includes(a.severity)) }));
  app.get(['/api/weather/current/', '/api/weather/forecast/', '/api/rainfall/'], async (req, res) => res.json(await fetchWeather(req.query)));
  app.get(['/api/location/search/', '/api/location/geocode/', '/api/shelters/location-search/', '/api/shelters/geocode/'], async (req, res) => res.json(await searchLocation(req.query)));
  app.get(['/api/weather/india/', '/api/weather/state/', '/api/weather/state/:code/'], async (req, res) => {
    const state = String(req.params.code || req.query.state || '').toLowerCase();
    const states = state ? locations.INDIAN_STATES_DATA.filter(s => s.code.toLowerCase() === state || s.name.toLowerCase() === state) : locations.INDIAN_STATES_DATA;
    if (!states.length) throw new HttpError(404, 'State not found.');
    const params = new URLSearchParams({ latitude: states.map(s => s.lat).join(','), longitude: states.map(s => s.lon).join(','), current: 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code', timezone: 'auto' });
    const result = await fetchJson(`https://api.open-meteo.com/v1/forecast?${params}`);
    const data = Array.isArray(result) ? result : [result];
    const hubs = states.map((s,i) => ({ ...s, city: s.capital, state: s.name, latitude: s.lat, longitude: s.lon, temperature: data[i]?.current?.temperature_2m, rainfall: data[i]?.current?.precipitation, wind_speed: data[i]?.current?.wind_speed_10m, humidity: data[i]?.current?.relative_humidity_2m, weather_code: data[i]?.current?.weather_code, is_available: !!data[i]?.current, risk: 'UNASSESSED', hazard: 'Weather observation; hazard assessment unavailable' }));
    res.json({ success: true, source: 'Open-Meteo', hubs, districts: hubs });
  });
  app.post('/api/risk/predict/', async (req, res) => {
    const result = await assess(req.body);
    // Store explicit assessments by signed-in users; passive public dashboard refreshes do not create records.
    if (req.identity && req.body.save === true) result.prediction = await repository.create('predictions', result.prediction);
    res.json(result);
  });
  app.get('/api/risk/zones/', async (req, res) => res.json({ success: true, zones: await repository.list('risk-zones') }));
  app.get('/api/population/exposure/', async (req, res) => listResult(res, await repository.list('population')));
  app.post('/api/evacuation/route/', async (req, res) => res.json(await route(req.body)));
  app.get(['/api/shelters/nearby/', '/api/shelters/recommend/'], async (req, res) => {
    const point = coordinates(req.query);
    const shelters = (await repository.list('shelters')).map(decorateShelter).filter(s => ['OPEN', 'NEAR_CAPACITY'].includes(s.status) && s.available_capacity > 0).map(s => ({ ...s, distance_km: +distance(point, s).toFixed(2) })).sort((a,b) => a.distance_km - b.distance_km);
    res.json({ success: true, shelters, results: shelters, recommended: shelters[0] || null, best_match: shelters[0] || null, recommendations: shelters, origin: point });
  });
  for (const kind of ['shelters', 'resources', 'rescue-teams', 'alerts', 'disasters', 'infrastructure']) {
    app.get(`/api/${kind}/`, async (req, res) => {
      const rows = await repository.list(kind);
      if (kind === 'shelters') res.json({ success: true, count: rows.length, shelters: rows.map(decorateShelter), results: rows.map(decorateShelter) });
      else listResult(res, rows);
    });
    app.post(`/api/${kind}/`, requireAdmin, async (req, res) => { const record = await repository.create(kind, validateRecord(kind, req.body)); res.status(201).json({ ...record, success: true }); });
    app.get(`/api/${kind}/:id/`, async (req, res) => {
      const row = (await repository.list(kind)).find(r => r.id === Number(req.params.id));
      if (!row) throw new HttpError(404, 'Record not found.');
      res.json(kind === 'shelters' ? decorateShelter(row) : row);
    });
    app.patch(`/api/${kind}/:id/`, requireAdmin, async (req, res) => {
      const row = (await repository.list(kind)).find(r => r.id === Number(req.params.id));
      if (!row) throw new HttpError(404, 'Record not found.');
      res.json(await repository.update(kind, row.id, validateRecord(kind, { ...row, ...req.body })));
    });
    app.delete(`/api/${kind}/:id/`, requireAdmin, async (req, res) => {
      if (!(await repository.remove(kind, Number(req.params.id))).length) throw new HttpError(404, 'Record not found.');
      res.status(204).end();
    });
  }
  app.post('/api/alerts/:id/dismiss/', requireAdmin, async (req, res) => {
    const row = (await repository.list('alerts')).find(r => r.id === Number(req.params.id));
    if (!row) throw new HttpError(404, 'Alert not found.');
    res.json({ success: true, alert: await repository.update('alerts', row.id, { ...row, is_active: false }) });
  });
  app.post('/api/shelters/:id/update-occupancy/', requireStaff, async (req, res) => {
    const row = (await repository.list('shelters')).find(r => r.id === Number(req.params.id));
    if (!row) throw new HttpError(404, 'Shelter not found.');
    const data = validateRecord('shelters', { ...row, current_occupancy: req.body.current_occupancy ?? req.body.occupancy });
    res.json({ success: true, shelter: await repository.update('shelters', row.id, data) });
  });
  async function runOrRequest(req, operation) {
    if (req.role === 'ADMIN') return { success: true, record: await repository.applyOperation(operation) };
    const request = await repository.create('approval-requests', { status: 'PENDING', requested_by: { id: req.identity.id, username: req.identity.email }, request_type: operation.action.toUpperCase(), target_model: operation.kind, target_object_id: operation.id, requested_changes: operation.changes || { quantity: operation.quantity }, operation, reason: String(req.body.reason || 'Operational request').slice(0,1000), created_at: new Date().toISOString() });
    return { success: true, pending: true, request };
  }
  app.post(['/api/resources/allocate/', '/resources/dispatch/'], requireStaff, async (req, res) => {
    const operation = { kind: 'resources', id: Number(req.body.resource_id), action: 'dispatch', quantity: Number(req.body.quantity), destination_zone: String(req.body.destination_zone || '').slice(0,200), actor: req.identity.id };
    if (!Number.isInteger(operation.quantity) || operation.quantity <= 0) throw new HttpError(400, 'Enter a positive whole-number quantity.');
    const result = await runOrRequest(req, operation);
    if (req.path.startsWith('/api/')) res.json(result); else res.redirect(303, '/resources/');
  });
  app.post('/resources/update-stock/', requireStaff, async (req, res) => {
    const row = (await repository.list('resources')).find(r => r.id === Number(req.body.resource_id));
    if (!row) throw new HttpError(404, 'Resource not found.');
    const quantity = Number(req.body.quantity_available ?? req.body.quantity);
    if (!Number.isInteger(quantity) || quantity < 0) throw new HttpError(400, 'Stock must be a nonnegative whole number.');
    await runOrRequest(req, { kind: 'resources', id: row.id, action: 'stock_update', changes: { quantity_available: quantity }, actor: req.identity.id });
    res.redirect(303, '/resources/');
  });
  app.post('/resources/team-status/', requireStaff, async (req, res) => {
    if (!['AVAILABLE','DEPLOYED','BUSY','OFFLINE'].includes(req.body.status)) throw new HttpError(400, 'Invalid team status.');
    await runOrRequest(req, { kind: 'rescue-teams', id: Number(req.body.team_id), action: 'team_status_update', changes: { status: req.body.status }, actor: req.identity.id });
    res.redirect(303, '/resources/');
  });
  app.post('/admin-dashboard/approvals/:id/:decision/', requireAdmin, async (req, res) => {
    const row = (await repository.list('approval-requests')).find(r => r.id === Number(req.params.id));
    if (!row) throw new HttpError(404, 'Approval request not found.');
    if (row.status !== 'PENDING') throw new HttpError(409, 'This request has already been reviewed.');
    if (req.params.decision === 'approve') await repository.applyOperation(row.operation, row.id);
    else if (req.params.decision === 'reject') await repository.rejectApproval(row.id, String(req.body.rejection_reason || '').slice(0,1000));
    else throw new HttpError(404, 'Unknown decision.');
    res.redirect(303, '/admin-dashboard/');
  });
  app.post('/api/alerts/request-change/', requireStaff, async (req, res) => {
    const action = req.body.requested_action;
    let operation;
    if (action === 'CREATE') operation = { kind: 'alerts', action: 'create', changes: validateRecord('alerts', req.body), actor: req.identity.id };
    else if (action === 'DEACTIVATE') operation = { kind: 'alerts', id: Number(req.body.alert_id), action: 'deactivate', changes: { is_active: false }, actor: req.identity.id };
    else throw new HttpError(400, 'Invalid alert request action.');
    const request = await repository.create('approval-requests', { status: 'PENDING', requested_action: action, request_type: 'ALERT_CHANGE', target_model: 'alerts', target_object_id: operation.id, requested_by: { id: req.identity.id, username: req.identity.email }, operation, reason: String(req.body.reason || '').slice(0,1000), created_at: new Date().toISOString() });
    res.status(201).json({ success: true, pending: true, request });
  });
  app.post('/api/admin/alert-requests/:id/review/', requireAdmin, async (req, res) => {
    const row = (await repository.list('approval-requests')).find(r => r.id === Number(req.params.id) && r.target_model === 'alerts');
    if (!row) throw new HttpError(404, 'Alert change request not found.');
    if (req.body.action === 'ALLOW') await repository.applyOperation(row.operation, row.id);
    else if (req.body.action === 'REJECT') await repository.rejectApproval(row.id, String(req.body.reason || '').slice(0,1000));
    else throw new HttpError(400, 'Invalid review action.');
    res.json({ success: true });
  });
  // Preserve admin form URLs and enforce server-verified privileges.
  app.post('/admin-dashboard/:kind/:action/', requireAdmin, async (req, res, next) => {
    if (req.params.action !== 'create') return next();
    const kind = req.params.kind === 'teams' ? 'rescue-teams' : req.params.kind;
    if (!['shelters', 'resources', 'rescue-teams', 'disasters', 'alerts'].includes(kind)) throw new HttpError(404, 'Unknown collection.');
    await repository.create(kind, validateRecord(kind, req.body));
    res.redirect(303, '/admin-dashboard/');
  });
  app.post('/admin-dashboard/:kind/:id/:action/', requireAdmin, async (req, res) => {
    const kind = req.params.kind === 'teams' ? 'rescue-teams' : req.params.kind;
    if (!['shelters', 'resources', 'rescue-teams', 'disasters', 'alerts'].includes(kind)) throw new HttpError(404, 'Unknown collection.');
    const row = (await repository.list(kind)).find(r => r.id === Number(req.params.id));
    if (!row) throw new HttpError(404, 'Record not found.');
    if (req.params.action === 'delete') await repository.remove(kind, row.id);
    else if (req.params.action === 'update') await repository.update(kind, row.id, validateRecord(kind, { ...row, ...req.body }));
    else throw new HttpError(404, 'Unknown action.');
    res.redirect(303, '/admin-dashboard/');
  });
  app.post('/api/assistant/chat/', async (req, res) => {
    const message = String(req.body.message || '').trim();
    if (!message || message.length > 2000) throw new HttpError(400, 'Enter a message of up to 2,000 characters.');
    const dataset = knowledge.DISASTER_KNOWLEDGE_DATA;
    const hazard = /cyclone|storm|wind/i.test(message) ? 'cyclone' : 'flood';
    const guide = dataset?.[hazard]?.safety_guide;
    const reply = guide ? `${hazard === 'cyclone' ? 'Cyclone' : 'Flood'} preparedness guidance:\n${guide.during.join('\n')}\nFor urgent help in India, call 112. Check official IMD and OSDMA updates for current warnings.` : 'For urgent help in India, call 112. Follow official local evacuation orders and check IMD/OSDMA advisories.';
    res.json({ success: true, reply, source: 'RUDRAM preparedness reference (rule-based guidance)', data_timestamp: new Date().toISOString() });
  });
  app.post('/api/assistant/analyze/', async (req, res) => res.json({ success: true, summary: 'Consult official warnings and verify local shelter availability before planning a response.', source: 'Preparedness guidance' }));
  const unavailable = (req, res) => res.status(503).json({ success: false, available: false, message: 'This service is not connected to a live provider in the Netlify deployment.', reply: 'This service is currently unavailable.' });
  app.all(['/api/satellite/{*path}', '/api/fire/{*path}', '/api/rainfall/gpm/', '/api/demo/{*path}'], unavailable);
  app.get('/api/infrastructure/water-bodies/', async (req, res) => res.json({ success: true, rivers: await repository.list('rivers'), dams: await repository.list('dams') }));
  app.get('/api/reports/export-csv/', requireStaff, async (req, res) => {
    const rows = await repository.list('disasters');
    const cell = value => '"' + String(value ?? '').replace(/^[=+@-]/, "'$&").replaceAll('"', '""') + '"';
    res.type('text/csv').attachment('rudram-incidents.csv').send(['id,name,disaster_type,severity,status', ...rows.map(r => [r.id,r.name,r.disaster_type,r.severity,r.status].map(cell).join(','))].join('\r\n'));
  });
  app.get('/api/reports/export-pdf/', requireStaff, async (req, res) => {
    const { default: PDFDocument } = await import('pdfkit');
    const rows = await repository.list('disasters');
    res.type('application/pdf').attachment('rudram-situation-report.pdf');
    const doc = new PDFDocument(); doc.pipe(res);
    doc.fontSize(20).text('RUDRAM Situation Report').fontSize(10).text(new Date().toISOString()).moveDown();
    if (!rows.length) doc.text('No incidents have been recorded.');
    for (const row of rows) doc.text(`${row.name || row.title || 'Incident'} | ${row.severity || ''} | ${row.status || ''}`).moveDown();
    doc.end();
  });
  app.get('/robots.txt', (req, res) => res.type('text/plain').send('User-agent: *\nAllow: /\nDisallow: /admin-dashboard/\nDisallow: /operator-dashboard/\nDisallow: /api/\n'));
  app.get('/sitemap.xml', (req, res) => {
    const origin = process.env.URL || 'https://earnest-tapioca-983975.netlify.app';
    res.type('application/xml').send(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${['dashboard','map','disasters_list','risk_prediction','alerts','shelters','evacuation','resources'].map(n => `<url><loc>${origin}${routes[n]}</loc></url>`).join('')}</urlset>`);
  });
  app.get('/logout/', (req, res) => res.type('html').send('<!doctype html><html lang="en"><meta charset="utf-8"><title>Signing out</title><body><p>Signing out…</p><script type="module">import {logout} from "https://esm.sh/@netlify/identity@2.0.1"; try { await logout(); } finally { location.replace("/"); }</script></body></html>'));
  app.get('/disasters/:id/', async (req, res, next) => {
    const disaster = (await repository.list('disasters')).find(r => r.id === Number(req.params.id));
    if (!disaster) return next(new HttpError(404, 'Incident not found.'));
    res.send(render('disasters/detail.html', { ...(await context(req)), disaster, timeline: [] }));
  });
  async function context(req) {
    const data = {};
    let databaseUnavailable = false;
    try {
      const rows = await Promise.all(collections.map(kind => repository.list(kind)));
      collections.forEach((kind,i) => { data[kind] = rows[i]; });
    } catch { databaseUnavailable = true; collections.forEach(kind => { data[kind] = []; }); }
    const shelters = data.shelters.map(decorateShelter);
    for (const rows of Object.values(data)) for (const row of rows) {
      for (const field of ['status','category','team_type','disaster_type','severity','request_type']) if (row[field] !== undefined) row[`get_${field}_display`] = String(row[field]).replaceAll('_',' ');
    }
    const alerts = data.alerts;
    const user = { is_authenticated: !!req.identity, is_superuser: req.role === 'ADMIN', is_staff: ['ADMIN','EMERGENCY_OPERATOR'].includes(req.role), username: req.identity?.user_metadata?.full_name || req.identity?.email || '', email: req.identity?.email, profile: { role: req.role }, get_full_name: req.identity?.user_metadata?.full_name || req.identity?.email || '' };
    return { user, USER_ROLE: req.role, user_role: req.role, request: { path: req.path, resolver_match: { url_name: pages[req.path]?.[1] || 'disaster_detail' } }, DEMO_MODE: false, APP_NAME: 'RUDRAM', APP_TAGLINE: 'Predict. Protect. Respond. Recover.', SITE_URL: process.env.URL || '', SEO_PAGE_TITLE: 'Disaster intelligence', DATA_SOURCE_LABEL: 'Recorded operations and on-demand live weather',
      messages: databaseUnavailable ? [{ tags: 'warning', message: 'Operational records are temporarily unavailable. Live weather and maps remain available.' }] : [],
      database_unavailable: databaseUnavailable, disasters: data.disasters, disasters_count: data.disasters.filter(d => d.status === 'ACTIVE').length, active_disaster: data.disasters[0], high_risk_zones_count: data['risk-zones'].filter(z => ['HIGH','CRITICAL'].includes(z.risk_level)).length,
      shelters, shelters_json: jsonForScript(shelters), available_shelters_count: shelters.filter(s => s.status === 'OPEN').length, alerts, active_alerts: alerts.filter(a => a.is_active), active_alerts_count: alerts.filter(a => a.is_active).length, ACTIVE_ALERTS_COUNT: alerts.filter(a => a.is_active).length,
      resources: data.resources, rescue_teams: data['rescue-teams'], rivers: data.rivers, dams: data.dams, zones: data['risk-zones'], population_zones: data.population, population_chart_data: [Math.max(0, data.population.reduce((s,p) => s + Number(p.total_population || 0) - Number(p.exposed_population || 0),0)), data.population.reduce((s,p) => s + Number(p.exposed_population || 0),0)],
      total_exposed_population: data.population.reduce((s,p) => s + Number(p.exposed_population || 0),0), infrastructure: data.infrastructure, latest_predictions: data.predictions, data_sources: [], DATA_SOURCES: [], audit_logs: data['audit-logs'], indian_states: locations.INDIAN_STATES_DATA,
      high_alerts: [], flood_summary: { available: false }, cyclone_summary: { available: false }, flood_locations_json: '[]', cyclone_locations_json: '[]', knowledge_data_json: jsonForScript(knowledge.DISASTER_KNOWLEDGE_DATA),
      approval_requests: data['approval-requests'].filter(r => r.requested_by?.id === req.identity?.id || req.role === 'ADMIN'), all_requests: data['approval-requests'], users: [], my_requests: data['approval-requests'].filter(r => r.requested_by?.id === req.identity?.id), operator_requests: req.role === 'ADMIN' ? data['approval-requests'].filter(r => r.status === 'PENDING') : [], pending_count: data['approval-requests'].filter(r => r.status === 'PENDING').length, pending_approvals_count: data['approval-requests'].filter(r => r.status === 'PENDING').length, pending_requests_count: 0,
      total_capacity: shelters.reduce((s,p) => s + Number(p.total_capacity || 0),0), total_occupancy: shelters.reduce((s,p) => s + Number(p.current_occupancy || 0),0), has_zone_data: !!data.population.length,
      total_shelter_cap: shelters.reduce((s,p) => s + Number(p.total_capacity || 0),0), total_shelter_occ: shelters.reduce((s,p) => s + Number(p.current_occupancy || 0),0), avail_shelter_cap: shelters.reduce((s,p) => s + p.available_capacity,0),
      total_cap: shelters.reduce((s,p) => s + Number(p.total_capacity || 0),0), total_occ: shelters.reduce((s,p) => s + Number(p.current_occupancy || 0),0), available_cap: shelters.reduce((s,p) => s + p.available_capacity,0), open_count: shelters.filter(s => ['OPEN','NEAR_CAPACITY'].includes(s.status)).length,
      total_avail: data.resources.reduce((s,r) => s + Number(r.quantity_available || 0),0), total_alloc: data.resources.reduce((s,r) => s + Number(r.quantity_allocated || 0),0), total_req: data.resources.reduce((s,r) => s + Number(r.quantity_required || 0),0),
      total_pop: data.population.reduce((s,p) => s + Number(p.total_population || 0),0), exposed_pop: data.population.reduce((s,p) => s + Number(p.exposed_population || 0),0), vulnerable_pop: data.population.reduce((s,p) => s + Number(p.vulnerable_population || 0),0), critical_pop: data.population.reduce((s,p) => s + Number(p.critical_risk_population || 0),0), shelter_deficit: data.population.reduce((s,p) => s + Number(p.shelter_deficit_count || 0),0),
    };
  }
  for (const [path, [template, name]] of Object.entries(pages)) {
    app.get(path, async (req, res) => {
      if (protectedPages.has(name) && !req.identity) return res.redirect('/login/');
      if (protectedPages.has(name) && !['ADMIN','EMERGENCY_OPERATOR'].includes(req.role)) throw new HttpError(403, 'Staff access is required.');
      if (name === 'admin_dashboard' && req.role !== 'ADMIN') throw new HttpError(403, 'Administrator access is required.');
      res.type('html').send(render(template, await context(req)));
    });
  }
  app.use('/api', (req, res) => res.status(404).json({ success: false, message: 'This API route is not available.', reply: 'This service is currently unavailable.' }));
  app.use((req, res) => res.status(404).type('html').send('<!doctype html><html lang="en"><title>Page not found | RUDRAM</title><h1>Page not found</h1><p><a href="/">Return to the dashboard</a></p></html>'));
  app.use((error, req, res, next) => {
    if (res.headersSent) return next(error);
    const status = error.status || 503;
    const message = error instanceof HttpError ? error.message : 'The service is temporarily unavailable. Please try again.';
    res.status(status).json({ success: false, error: message, message, detail: message, reply: message });
  });
  return app;
}
export { pages, validateRecord };
