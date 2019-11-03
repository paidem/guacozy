Guacozy can be used with multiple **guacd** servers, 
which is convenient when you have isolated environments, 
where you place **guacd** inside and only allow 
guacozy >> guacd in firewall.  

This way you don't have to create multiple rules guacozy >> servers

Later you add _**guacd server**_ in Administration and refer to it 
when specifying a _**Connection**_

### Docker
To start additional guacd you can use docker 
```
docker run --restart always -p 4822:4822 guacamole/guacd
```
### CentOS
Or if you are on CentOS 7 you can use epel-release
```
yum install epel-release
yum install guacd

# Enable guacd to listen on all (or specify desired) interfaces
# By defaut guacd listens on 127.0.0.1

echo "OPTS='-l 4822 -b 0.0.0.0'" >> /etc/sysconfig/guacd

# Enable/start
systemctl enable --now guacd

# Check status
systemctl status guacd

# Check that guacd is listening
netstat -pteln | grep guacd
```

### Build from sources
If you feel adventurous, you can build guacamole from sources and use guacd from build.
  
Follow [official documentation here](https://guacamole.apache.org/doc/gug/installing-guacamole.html)