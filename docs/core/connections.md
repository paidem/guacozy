Connection object describes a VNC/RDP/SSH connection.  
##### Options
It allows to specify most of connection options allowed by Apache Guacamole protocol for selected protocol 
([read more](https://guacamole.apache.org/doc/gug/configuring-guacamole.html#connection-configuration))

Connection options/credentials are never exposed to application user, who doesn't have staff permission level.  
This means you can create connection with a name, but all other information hidden from user (host, port, credentials) 
  
##### Hierarchy
Connection must have a parent (Folder)

##### Permission
You cannot specify permissions at connection level, only folder-level permissions are implemented.   

##### Connection credentials
You can specify **username, domain, password, private key, passphrase** directly in connection object.   

You can reference a **Static Credentials** object if this connection uses a password shared with other servers.  

You can reference a **Named Credentials** object if every user should have own credentials to this connection (**Personal Named Credentials**) 
