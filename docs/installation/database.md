The database connection settings  is passed using `DJANGO_DB_URL` environment variable which conforms to django-environ standarts 
You can find documentation here: https://django-environ.readthedocs.io/en/latest/#django-environ

Container build includes drivers for SQLite and PostgreSQL (psycopg2)

### Examples:  
#### SQLite
SQLite located in the same directory as guacozy_server manage.py
```
sqlite:///guacozydb.sqlite3
```
#### PostgreSQL
PostgreSQL located on server `db`, listening on port `5432`, using user `postgres` , no password and database name `postgres` 
```
DJANGO_DB_URL=postgres://postgres@db:5432/postgres
```

PostgreSQL located on server `postdb.example.com`, listening on port `5432`, using user `guacozy_app` , password `Passw0rd` and database name `guacozy_db` 
```
DJANGO_DB_URL=postgres://guacozy_app:Passw0rd@postdb.example.com:5432/guacozy_db
```
