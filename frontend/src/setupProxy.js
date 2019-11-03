const proxy = require('http-proxy-middleware');

let proxy_location = '';

if (process.env.DJANGO_PROXY_HOST && process.env.DJANGO_PROXY_PORT){
  proxy_location=process.env.DJANGO_PROXY_HOST + ":" + process.env.DJANGO_PROXY_PORT;
}
else{
  proxy_location='localhost:8000';
}

module.exports = function(app) {
  app.use(proxy('/api', { target: 'http://' + proxy_location } ));
  app.use(proxy('/tunnelws', { target: 'ws://'  + proxy_location, ws: true }));
  app.use(proxy('/admin', { target: 'http://' +  proxy_location }));
  app.use(proxy('/accounts', { target: 'http://'  + proxy_location }));
  app.use(proxy('/staticfiles', { target: 'http://'  + proxy_location}));
};
