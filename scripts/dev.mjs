import app from '../netlify/server/index.mjs';
const server = app.listen(process.env.PORT || 3000, '0.0.0.0');
for (const signal of ['SIGTERM', 'SIGINT']) process.on(signal, () => server.close(() => process.exit(0)));
