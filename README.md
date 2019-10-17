# guacozy
__Cozy server administration tool based on [Apache Guacamole™](https://guacamole.apache.org/)__

##Links
[guacozy-server on Dockerhub](https://hub.docker.com/r/guacozy/guacozy-server)

##Notes

###Encryption

To use password fields encryption you need to specify `FIELD_ENCRYPTION_KEY` environment variable  
Generate encryption key with management command:  

`python ./manage.py generate_encryption_key`  

If it is lost, password fields in the database will be unusable