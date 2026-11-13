import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { createApp, pages, validateRecord } from '../web/app.mjs';
import { render } from '../web/render.mjs';
import { predictProbability } from '../web/risk.mjs';
import { coordinates } from '../web/services.mjs';
import cases from './model-parity.json' with { type: 'json' };

const emptyRepository = { list: async () => [], healthy: async () => true };
async function serve(t, repository = emptyRepository, options = {}) {
  const server = createApp(repository, options).listen(0, '127.0.0.1');
  await new Promise(resolve => server.once('listening', resolve));
  t.after(() => new Promise(resolve => server.close(resolve)));
  return (path, init) => fetch(`http://127.0.0.1:${server.address().port}${path}`, init);
}
test('portable flood ensemble matches Python estimators for 30 feature vectors', () => {
  for (const fixture of cases) assert.ok(Math.abs(predictProbability(fixture.input) - fixture.expected) < 1e-6);
});
test('coordinate validation rejects missing, nonnumeric and out-of-range inputs', () => {
  for (const data of [{}, {lat: '',lon: 1}, {lat:'abc',lon:0}, {lat:91,lon:0}, {lat:0,lon:181}]) assert.throws(() => coordinates(data));
  assert.deepEqual(coordinates({lat:0,lon:0}), {latitude:0,longitude:0});
});
test('shelter records enforce capacity and occupancy invariants', () => {
  assert.throws(() => validateRecord('shelters',{ name:'Test', total_capacity:10,current_occupancy:11 }));
  assert.throws(() => validateRecord('resources',{ quantity_available:-1 }));
  const record = validateRecord('shelters',{ name:'Test',total_capacity:10,current_occupancy:0,id:500 });
  assert.equal(record.status,'OPEN'); assert.equal(record.id, undefined);
});
test('every existing page renders and its inline scripts parse with an empty database', async t => {
  const request = await serve(t, emptyRepository, {authenticate: async () => ({id:'test-admin',email:'admin@example.test',app_metadata:{roles:['ADMIN']}})});
  for (const path of Object.keys(pages)) {
    const response = await request(path);
    assert.equal(response.status,200,path);
    const html = await response.text();
    assert.ok(!html.includes('{%'), path);
    for (const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)) {
      if (/type=["'](?:application\/[^"']+|module)/i.test(match[1])) continue;
      assert.doesNotThrow(() => new vm.Script(match[2],{filename:path}),path);
    }
  }
});
test('pages and API distinguish unavailable database from empty records', async t => {
  const request = await serve(t, {...emptyRepository, list: async () => {throw new Error('database unavailable');},healthy:async()=>{throw new Error('database unavailable');}});
  assert.equal((await request('/api/health/')).status,503);
  assert.equal((await request('/api/shelters/')).status,503);
  const response = await request('/'); assert.equal(response.status,200);
  assert.ok((await response.text()).includes('Operational records are temporarily unavailable'));
});
test('public visitors cannot change operations, self-assign roles or access admin pages', async t => {
  const request = await serve(t);
  assert.equal((await request('/api/shelters/',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})).status,401);
  assert.equal((await request('/api/resources/allocate/',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})).status,401);
  assert.equal((await request('/admin-dashboard/',{redirect:'manual'})).status,302);
  assert.equal((await request('/switch-role/?role=ADMIN')).status,404);
});
test('citizens cannot acquire staff privileges through user metadata', async t => {
  const request = await serve(t, emptyRepository, {authenticate:async()=>({id:'citizen',user_metadata:{role:'ADMIN'}})});
  assert.equal((await request('/api/shelters/',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})).status,403);
});
test('operator dispatch creates an approval request without changing stock', async t => {
  const created = [];
  const request = await serve(t, {...emptyRepository, create:async(kind,data)=>{created.push({kind,data});return {id:1,...data};},applyOperation:async()=>{throw new Error('Stock must not change');}}, {authenticate:async()=>({id:'operator',email:'operator@example.test',app_metadata:{roles:['EMERGENCY_OPERATOR']}})});
  const response = await request('/api/resources/allocate/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({resource_id:1,quantity:5,destination_zone:'Test'})});
  assert.equal(response.status,200);assert.equal((await response.json()).pending,true);assert.equal(created[0].kind,'approval-requests');
});
test('cross-origin writes are rejected before mutation', async t => {
  const request = await serve(t);
  const response = await request('/api/assistant/chat/',{method:'POST',headers:{'Content-Type':'application/json',Origin:'https://untrusted.example'},body:JSON.stringify({message:'flood'})});
  assert.equal(response.status,403);
});
test('live routes pass validated provider responses and unavailable services report failure', async t => {
  const request = await serve(t,emptyRepository,{fetchWeather:async input => ({success:true,latitude:Number(input.latitude),current:{temperature:28}})});
  assert.equal((await (await request('/api/weather/current/?latitude=20&longitude=85')).json()).current.temperature,28);
  assert.equal((await request('/api/satellite/flood-detection/',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})).status,503);
  const chat = await (await request('/api/assistant/chat/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:'cyclone'})})).json();
  assert.match(chat.reply,/112/); assert.match(chat.source,/rule-based/);
});
test('weather separates historical observations from future forecast hours', async t => {
  const { weather } = await import('../web/services.mjs');
  t.mock.method(globalThis, 'fetch', async () => Response.json({
    elevation: 30, timezone: 'Asia/Kolkata',
    current: { time:'2026-11-13T12:00',temperature_2m:28,relative_humidity_2m:80,precipitation:2,weather_code:80,wind_speed_10m:10,wind_gusts_10m:15 },
    hourly: { time:['2026-11-12T12:00','2026-11-13T11:00','2026-11-13T12:00','2026-11-13T13:00'],precipitation:[3,4,5,6],temperature_2m:[25,26,27,28],relative_humidity_2m:[80,80,80,80],wind_speed_10m:[10,10,10,10] },
    daily: {time:['2026-11-12','2026-11-13','2026-11-14'],precipitation_sum:[7,8,9]}
  }));
  const result = await weather({latitude:20,longitude:85});
  assert.equal(result.hourly.time[0], '2026-11-13T12:00');
  assert.equal(result.daily.time[0], '2026-11-13');
  assert.equal(result.current.rainfall_24h, 7);
  assert.equal(result.current.condition, 'Rain');
  assert.equal(result.historical_hourly.time.length,2);
});
test('template JavaScript escaping protects quoted names in inline attributes', () => {
  const html = render('resources/index.html',{request:{path:'/resources/',resolver_match:{}},user:{},user_role:'ADMIN',USER_ROLE:'ADMIN',resources:[{id:1,name:'O\'Brien "Camp"',quantity_available:5}],rescue_teams:[]});
  assert.ok(html.includes('O\\u0027Brien \\u0022Camp\\u0022'));
  assert.ok(!html.includes("quickAllocateItem(1, 'O'Brien"));
});
