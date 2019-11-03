These are environment variables which you can specify when starting guacozy-server:
  
`DEBUG` : Django DEBUG mode  

`DJANGO_ALLOWED_HOSTS`: Let's you specify allowed hosts to prevent host header attacks 
([Read more](https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts))


`DJANGO_SECRET_KEY` : random string used for hashing (50 chars)  

`FIELD_ENCRYPTION_KEY` - encryption key which will be used to encrypt passwords in database [Read more](running-in-production.md)  

`DJANGO_TIME_ZONE` : timezone (e.g. Europe/Vilnius)

`DJANGO_DB_URL` : DB URL - read at [django-environ documentation](https://django-environ.readthedocs.io/en/latest/index.html)


`SUPERUSER_NAME`,`SUPERUSER_EMAIL`,`SUPERUSER_PASSWORD` : use these if you want default admin to have specified values  

If you don't specify `SUPERUSER_` values, user **admin** with password **admin** 
and email **admin@example.com** will be created.  
You can always change admin's email/password later, 
however if you ever delete "admin" user it will be recreated on next startup.  
So if you are unhappy with **admin** username, specify just it (you can specify name/email and skip password)