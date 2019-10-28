# Running guacozy using docker-compose

## Step 1
Create empty directory and add docker-compose.yml  

If this is a production environment, make appropriate changes:
- change DJANGO_SECRET_KEY to some other value (50 or more symbols).   
DJANGO_SECRET_KEY is injected using django-environ, which has some problems with special characters
- 
```
# docker-compose.yml

version: '3'  
services:
  server:
    image: guacozy/guacozy-server
    restart: always
    depends_on:
      - db
    volumes:
      - staticfiles:/app/staticfiles/
    environment:
      - DJANGO_SECRET_KEY=abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz
      - FIELD_ENCRYPTION_KEY=qjq4ObsXMqiqQyfKgD-jjEGm4ep8RaHKGRg4ohGCi1A=
      - DJANGO_DB_URL=postgres://postgres@db:5432/postgres
    ports:
      - 8080:80
      - 8443:443
  guacd:
    image: linuxserver/guacd
    restart: always
  db:
    image: postgres:10.4-alpine
    restart: always
    volumes:
    - postgres-data:/var/lib/postgresql/data
volumes:
  staticfiles:
  postgres-data:
```
