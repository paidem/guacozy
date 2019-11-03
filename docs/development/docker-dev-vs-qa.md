Development docker-compose is very different from final build:

In development build

- Django is run using `manage.py runserver` which is not suitable for production, listens on port `8000`
- React is run using `npm run start` - NodeJS development server, listens on port `3000`
- Static files are served by their appropriate servers (`/statifiles/` in Django and `/static` in React)


In production build:

- Django is run using Daphne, which listens on sock file (`/run/daphne/daphne%(process_num)d.sock`)
- React application is served as a static files (`.js/.css`) using Nginx
- Nginx proxies request for Django to sock file. 


If you want to build container with same Dockerfile as official to test how application will run in productions,
 use just default Dockerfile (`docker build`) or use included `docker-compose-qa.yml` file 
 which contains app/db/guacd stack

```
docker-compose -f docker-compose-qa.yml up
```