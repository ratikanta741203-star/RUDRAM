import nunjucks from 'nunjucks';
import templates from './templates.json' with { type: 'json' };

export const routes = {
  home: '/', dashboard: '/dashboard/', map: '/map/', disasters_list: '/disasters/',
  risk_prediction: '/risk/', population: '/population/', drone_view: '/drone-view/',
  alerts: '/alerts/', evacuation: '/evacuation/', shelters: '/shelters/', resources: '/resources/',
  assistant: '/assistant/', satellite: '/satellite/', reports: '/reports/', settings: '/settings/',
  login: '/login/', citizen_signup: '/citizen/signup/', logout: '/logout/',
  admin_dashboard: '/admin-dashboard/', operator_dashboard: '/operator-dashboard/',
  resource_dispatch: '/resources/dispatch/', resource_update_stock: '/resources/update-stock/',
  team_status_update: '/resources/team-status/',
};
export function url(name, id) {
  if (name === 'disaster_detail') return `/disasters/${id}/`;
  if (name === 'admin_approval_approve') return `/admin-dashboard/approvals/${id}/approve/`;
  if (name === 'admin_approval_reject') return `/admin-dashboard/approvals/${id}/reject/`;
  if (name.startsWith('admin_')) {
    const match = name.match(/^admin_(shelter|resource|team|disaster|alert)_(create|update|delete)$/);
    if (match) return `/admin-dashboard/${match[1]}s/${match[2] === 'create' ? 'create' : id + '/' + match[2]}/`;
  }
  return routes[name] || `/api/unsupported/${name}/`;
}
export function translate(source) {
  return source
    .replace(/{%\s*(?:load\s+[^%]+|csrf_token)\s*%}/g, '')
    .replace(/{%\s*url\s+(['"])([^'"]+)\1([^%]*)%}/g, (_, q, name, args) => `{{ url('${name}'${args.trim() ? ', ' + args.trim() : ''}) }}`)
    .replace(/{%\s*now\s+[^%]+%}/g, String(new Date().getFullYear()))
    .replace(/{%\s*empty\s*%}/g, '{% else %}')
    .replace(/{%\s*with\s+([^%]+)%}/g, '{% set $1 %}')
    .replace(/{%\s*endwith\s*%}/g, '')
    .replace(/\|([a-z_]+):("[^"]*"|'[^']*'|[\w.]+)/g, '|$1($2)')
    .replace(/forloop.counter0/g, 'loop.index0').replace(/forloop.counter/g, 'loop.index')
    .replace(/\bTrue\b/g, 'true').replace(/\bFalse\b/g, 'false').replace(/\bNone\b/g, 'none');
}
class TemplateLoader extends nunjucks.Loader {
  getSource(name) {
    if (!Object.hasOwn(templates, name)) return null;
    return { src: translate(templates[name]), path: name, noCache: false };
  }
}
export const environment = new nunjucks.Environment(new TemplateLoader(), { autoescape: true });
environment.addGlobal('url', url);
environment.addFilter('floatformat', (value, digits = 1) => Number(value || 0).toFixed(Number(digits)));
environment.addFilter('escapejs', value => new nunjucks.runtime.SafeString(String(value ?? '').replace(/[\\'"<>&=;\u0000-\u001f\u2028\u2029]/g, char => '\\u' + char.charCodeAt(0).toString(16).padStart(4, '0'))));
environment.addFilter('timesince', value => value ? `${Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 60000))} minutes` : 'No data');
environment.addFilter('date', value => value ? new Date(value).toLocaleString('en-IN') : '');
environment.addFilter('truncatewords', (value, count) => String(value || '').split(/\s+/).slice(0, Number(count)).join(' '));
environment.addFilter('json_script', (value, id) => new nunjucks.runtime.SafeString(`<script type="application/json" id="${nunjucks.lib.escape(id)}">${JSON.stringify(value ?? []).replace(/</g, '\\u003c')}</script>`));
// Django's default filter also substitutes empty strings and zero.
environment.addFilter('default', (value, fallback) => value || fallback);
export function render(name, context) { return environment.render(name, context); }
