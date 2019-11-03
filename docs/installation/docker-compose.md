## Step 0
Make sure you have docker-compose
```
docker-compose --version
```
or install docker-compose [here](https://docs.docker.com/compose/install/)

## Step 1
Create empty directory (e.g. named "guacozy") and add `docker-compose.yml`

```yaml
# docker-compose.yml

version: '3'  
services:
  server:
    image: guacozy/guacozy-server
    restart: always
    depends_on:
      - db
    environment:
      - DJANGO_SECRET_KEY=abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz
      - FIELD_ENCRYPTION_KEY=qjq4ObsXMqiqQyfKgD-jjEGm4ep8RaHKGRg4ohGCi1A=
      - DJANGO_DB_URL=postgres://postgres@db:5432/postgres
      - DJANGO_ALLOWED_HOSTS=*
    ports:
      - 10080:80
      - 10443:443
  guacd:
    image: linuxserver/guacd
    restart: always
  db:
    image: postgres:10.4-alpine
    restart: always
    volumes:
    - postgres-data:/var/lib/postgresql/data
volumes:
  postgres-data:
```

Adjust environment variables (refer [Environment variables](environment-variables.md) section)
## Step 2
Open shell in the directory hosting docker-compose.yml file and start stack in attached mode   
```
docker-compose up
```
Read the logs.   
Access the application:  
- https://127.0.0.1:10443 (if you run docker on local linux/mac machine)
- https://192.168.99.100:10443 (if you run docker on windows. You can get the IP using `docker-machine ip` command)
- https://your-docker-host:10443 (if you are running it on a dedicated docker host/VM)

In case of problems read [Troubleshooting](troubleshooting.md) section.

## Step 3
Try to login using default username/password:  
username: **admin**  
password: **admin**

## Step 4
If everything seems right, shutdown application by pressing Ctrl+C once (in terminal where docker-compose is running) and start in detached mode:
```
docker-compose up -d
```