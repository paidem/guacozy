Guacozy can be run using Træfik reverse proxy

This is an example when Træfik is configured to use [docker as backend](https://docs.traefik.io/v1.4/configuration/backends/docker/)  
All træfik config is done using labels in container  
There is a network `proxy` which is used as a network connecting træfik to backend servers.

### Changes to docker-compose
Use external network (network is called `proxy` in this example) for `server` service
```
services:
  server:
    networks:
      - default
      - proxy
...

...
networks:
  proxy:
      external: true
```  
Specify træfik labels to automatically configure new frontend/backend in træfik  

```
    labels:
      traefik.port: 80
      traefik.enable: true
      traefik.frontend.rule: guacozy.example.com
```
Specify `DJANGO_ALLOWED_HOSTS` to be the same as host in træfik frontend
```
    environment:
      - DJANGO_ALLOWED_HOSTS=guacozy.example.com
```

### Working example
```
version: '3'
services:
  server:
    image: guacozy/guacozy-server
    restart: always
    depends_on:
      - db
    volumes:
      - ./config/ssl:/ssl/
      - ./config/ldap_config.py:/app/guacozy_server/ldap_config.py
    networks:
      - default
      - proxy
    labels:
      traefik.port: 80
      traefik.enable: true
      traefik.frontend.rule: guacozy.example.com
    environment:
      - DJANGO_SECRET_KEY=abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz
      - FIELD_ENCRYPTION_KEY=qjq4ObsXMqiqQyfKgD-jjEGm4ep8RaHKGRg4ohGCi1A=
      - DJANGO_DB_URL=postgres://postgres@db:5432/postgres
      - DJANGO_ALLOWED_HOSTS=guacozy.example.com
      - DEBUG=False
  guacd:
    image: guacamole/guacd
    restart: always
    networks:
      - default
  db:
    image: postgres:10.4-alpine
    restart: always
    volumes:
      - ./data/postgres-data:/var/lib/postgresql/data
    networks:
      - default

networks:
  proxy:
      external: true
```
