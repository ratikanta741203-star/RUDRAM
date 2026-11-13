# RUDRAM

Disaster intelligence and response coordination, adapted to run on Netlify with Node.js 24, Netlify Database, and Netlify Identity. The existing Django application remains in the repository for reference and model tooling; it is no longer the deployed web runtime.

## Run locally

Install Node.js 24 and run `npm ci`, then `npm run dev` with the Netlify CLI available. Open http://localhost:8889. `npm test` checks page rendering, inline JavaScript, access control, validation, and prediction parity.

Netlify detects `netlify/server/index.mjs` automatically. Static assets are published from `static/`, while the server renders pages and handles APIs. No Python, Gunicorn, MySQL server, or Python child process is needed by the deployed app.

## Data and accounts

Operational records are stored in Netlify Database using Drizzle. The schema is defined in `db/schema.ts`; generated migrations are in `netlify/database/migrations/`. Netlify applies them automatically during deployment. Until the first migration is applied, record APIs and health checks return an unavailable status, while pages display a database notice. Do not apply migrations manually.

The database starts empty. Shelters, resources, rescue teams, incidents, and website alerts can be created in the admin command center. Accounts use Netlify Identity email signup and confirmation. Trusted `app_metadata.roles` values `ADMIN` and `EMERGENCY_OPERATOR` control staff access. A signup cannot choose its own role. Existing Django users and MySQL records are not automatically imported. Identity accounts and staff roles are managed through Netlify Identity.

Resource dispatch requests from operators require administrator review. Applying a dispatch locks the stock record and updates stock, audit history, and approval status in one database transaction. Website alerts do not send SMS, sirens, or radio broadcasts.

## Integrations and predictions

Weather and forecasts come from Open-Meteo, location search uses Open-Meteo and OpenStreetMap, and road directions use OSRM. Upstream outages return explicit errors. Road routing does not verify flood conditions or road closures.

The flood estimator runs portable versions of the repository's trained XGBoost and Random Forest models. Thirty exported reference cases match Python probabilities to within 0.000001. Estimates are experimental; hydrological features without observations use disclosed assumptions, and the interface does not invent a calibrated confidence score. Cyclone inference has not been ported. The preparedness assistant uses the existing reference guidance and is explicitly rule-based.

Satellite analysis, FIRMS fire feeds, GPM rainfall, drone telemetry, and demo scenarios are not connected in the Netlify runtime. Satellite/fire/GPM/demo APIs return unavailable responses rather than simulated results. Additional integrations require separate implementation.

## Maintaining the adapter

`web/app.mjs` contains the Netlify routes and `db/index.mjs` handles persistence. `web/render.mjs` adapts the existing template syntax. After changing files in `templates/` or geographic reference data, run `python scripts/sync-templates.py` to refresh importable template snapshots used by the server bundle. After intentionally replacing the trusted trained estimators, run `python scripts/export-models.py` with the Python model dependencies installed and rerun `npm test`.
