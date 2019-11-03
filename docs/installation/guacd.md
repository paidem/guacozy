guacd is the Guacamole daemon component which does the heavy lifting of connecting to VNC/RDP/SSH

Sometime you will want do have several guacd servers
 (e.g. if you have several customers - you can install guacd in customers network 
 and connection to guacd is the only connection needed from your network. 
 On the customer's side you will need firewall rules from guacd to other servers using VNC/RDP/SSH)

When using docker-compose - add a guacd service in your stack
```
  guacd:
    image: guacamole/guacd
    restart: always
```
When running in docker-compose you do not have to expose port, as other containers will have access to it under DNS name `guacd` 

Or if you want to run it in a different host - you can run it as a standalone container
```
docker run --name guacdlocal --restart always -d -p 4822:4822 guacamole/guacd
```

List of alternative docker images with guacd  
[Glyptodon guacd](https://hub.docker.com/r/glyptodon/guacd)   
[Official guacamole guacd](https://hub.docker.com/r/guacamole/guacd)   
[Linuxserver guacd](https://hub.docker.com/r/linuxserver/guacd)  