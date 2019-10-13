const proxy = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(proxy('/api', { target: 'http://localhost:8000' }));
  app.use(proxy('/api-auth', { target: 'http://localhost:8000' }));
  app.use(proxy('/tunnelws', { target: 'ws://localhost:8000', ws: true }));
  app.use(proxy('/admin', { target: 'http://localhost:8000' }));
  app.use(proxy('/accounts', { target: 'http://localhost:8000' }));
  app.use(proxy('/djstatic', { target: 'http://localhost:8000'}));
};
