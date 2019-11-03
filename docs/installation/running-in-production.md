If this is a production environment, make appropriate changes:

### Provide custom SSL certificates
You can provide your own certificates, read more in [SSL section](https://guacozy.readthedocs.io/en/latest/installation/ssl/)

### Change published ports
In the example we user ports 10080 and 10443  
In productions you may want other ports and disable HTTP altogether because of security concerns

### Disable HTTP port 
Clipboard reading is available only on HTTPS ports when using host other than localhost, 
so if you want to use clipboard sync feature, you will need to access via HTTPS

### Change DJANGO_SECRET_KEY 
Change to some other value (50 or more symbols, dont' use '$' symbol as it will try to expand variable).

### Change FIELD_ENCRYPTION_KEY
If you don't change FIELD_ENCRYPTION_KEY, the key from example will be used (bad idea).   
If you don't specify FIELD_ENCRYPTION_KEY, on application start you will be notified (in container logs) about this, 
and a new key will be generated on each start, which means your saved password will not work after restart.  
  
You can use the suggested value (in container logs) or you can generate one at any time using `generate_encryption_key` management command

If you started using docker compose:   
```
docker-compose exec server ./manage.py generate_encryption_key
``` 

If you have not started guacozy-server container
```
# if you don't have container running
docker run -it --rm guacozy/guacozy-server python /app/manage.py generate_encryption_key
``` 
