The database connection settings  is passed using `DJANGO_DB_URL` environment variable which conforms to django-environ standards 
You can find documentation here: https://django-environ.readthedocs.io/en/latest/#django-environ

Container build includes drivers for SQLite and PostgreSQL (psycopg2)

### DB in docker-compose
The easiest way when running inside a container - run a stack with docker-compose which includes PostgreSQL container.  
For this you specify a service named `db`, and link to it using connection string  `DJANGO_DB_URL=postgres://postgres@db:5432/postgres`
Mount PostgreSQL data folder to named  volume or bind mount.

##### Using named volume
```
version: '3'
services:
  server:
    image: guacozy/guacozy-server
    restart: always
    depends_on:
      - db
    environment:
    - DJANGO_DB_URL=postgres://postgres@db:5432/postgres
...
  db:
    image: postgres:10.4-alpine
    restart: always
    volumes:
    - postgres-data:/var/lib/postgresql/data
...
volumes:
  postgres-data:
```

##### Using bind mount
Bind mount postgresql data to directory `./data/postgres`
```
version: '3'
services:
  server:
    image: guacozy/guacozy-server
    restart: always
    depends_on:
      - db
    environment:
    - DJANGO_DB_URL=postgres://postgres@db:5432/postgres
...
  db:
    image: postgres:10.4-alpine
    restart: always
    volumes:
    - ./data/postgres:/var/lib/postgresql/data
```

### Connection string examples
##### SQLite
SQLite file `guacozydb.sqlite3` located in the same directory as guacozy_server manage.py
```
sqlite:///guacozydb.sqlite3
```

SQLite file `guacozydb.sqlite3` located under `/datafiles/` (note the four slashes)
```
sqlite:////datafiles/guacozydb.sqlite3
```
##### PostgreSQL
PostgreSQL located on server `db`, listening on port `5432`, using user `postgres` , no password and database name `postgres` 
```
DJANGO_DB_URL=postgres://postgres@db:5432/postgres
```

PostgreSQL located on server `postdb.example.com`, listening on port `5432`, using user `guacozy_app` , password `Passw0rd` and database name `guacozy_db` 
```
DJANGO_DB_URL=postgres://guacozy_app:Passw0rd@postdb.example.com:5432/guacozy_db
```
