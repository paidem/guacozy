Comfortable development process includes running two separate servers:

- Django runserver (`python manage.py runserver`) on port **8000**
- React NodeJS development server (`npm run start`) on port **3000**

Those two servers have file monitoring and automatic reload/live patch on code change.

### PyCharm IDE
If you develop on in IDE such as PyCharm, start 2 PyCharm instances and open each project in different directories  
#### Open PyCharm in project root  

Create virtualenv interpreter with Python 3.7     
Configure run command as "python ./manage.py runserver"   

Environment:   
`PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=guacozy_server.settings`
    
#### Open PyCharm in /frontend/

Configure run command as `npm run start`

#### Initialize database
Run
```
# Migrate database. Run once to initialize database and after you add any migrations
python ./manage.py migrate

# Create superuser
python ./manage.py createsuperuser

# Optional. Initialize default guacd server reference
python ./manage.py  initguacd

# Optional. Initialize user groups
python ./manage.py  initgroups

# Optional Generate new field encryption key to use in FIELD_ENCRYPTION_KEY value
python ./manage.py generate_encryption_key

```

#### Connect to development servers
Connect to http://localhost:3000/ to open React App  
Connect to http://localhost:8000/admin/ to open Django Admin  

Calls to django urls (`/admin/`, `/api/`, `/tunnelws/`) will be proxied by react development server (see `frontend/src/setupProxy.js`)

### Docker-compose
#### Start stack
You can also start development environment as a docker compose stack.

Inside project root run 
```
docker-compose up --build
```
This will create a stack of containers:
- django
- react
- db
- guacd

On build:  
- Django container on build will copy requirements*.txt files and install Python dependencies using `pip install -r`
- React container will copy `package.json` and `package-lock.json` and install dependencies using `npm install`

On docker-compose up:
- Django container will have `/guacozy_server/` mounted as `/app/`
- React container will have `/frontend/` mounted as `/frontend/`

After starting you have to initialize database (migration) and create superuser  
Open another terminal and go to project folder.  

#### Initialize database

Run
```
# Migrate database. Run once to initialize database and after you add any migrations
docker-compose exec django python ./manage.py migrate

# Create superuser
docker-compose exec django python ./manage.py createsuperuser

# Optional. Initialize default guacd server reference
docker-compose exec django python ./manage.py  initguacd

# Optional. Initialize user groups
docker-compose exec django python ./manage.py  initgroups

# Optional Generate new field encryption key to use in FIELD_ENCRYPTION_KEY value
docker-compose exec django python ./manage.py generate_encryption_key

```
#### Connect to development servers
Connect to http://localhost:3000/ to open React App  
Connect to http://localhost:8000/admin/ to open Django Admin 

Calls to django urls (`/admin/`, `/api/`, `/tunnelws/`) will be proxied by react development server (see `frontend/src/setupProxy.js`)