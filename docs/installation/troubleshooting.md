#### Bad Request (400)

Check `DJANGO_ALLOWED_HOSTS` environment variable. 
It must be either `*` to allow all hosts or be a comma separated list of hosts which can be used to access your installation (can be just one host)

#### Found another file with the destination path ...
When starting you see messages in log:
```
Found another file with the destination path 'admin/js/prepopulate.js'. It will be ignored since only the first encountered file is collected. If this is not what you want, make sure every static file has a unique path.
Found another file with the destination path 'admin/js/timeparse.js'. It will be ignored since only the first encountered file is collected. If this is not what you want, make sure every static file has a unique path.
```

This is normal, as `grapelli` django admin uses same static files names as `django.contrib.admin` (default django admin)


####  Name does not resolve
You cannot open a RDP/VNC/SSH connections and in logs you see message:
```
2019-10-28 09:13:19,494 ERROR Exception inside application: [Errno -2] Name does not resolve

File "/usr/local/lib/python3.7/socket.py", line 707, in create_connection
for res in getaddrinfo(host, port, 0, SOCK_STREAM):
File "/usr/local/lib/python3.7/socket.py", line 748, in getaddrinfo
for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
[Errno -2] Name does not resolve
```

This means that Guacozy cannot connect to **guacd** server.  

When application starts a default _**Guacd Server**_  is created with `hostname=guacd` and `port=4822` .   
This _**Guacd Server**_  is set as a default in _**Application Settings**_

If you are not running docker-compose with "guacd" service you have to specify your own guacd server 
by creating a new _**Guacd Server**_ object and setting it as default in _**Application Settings**_