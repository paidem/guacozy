To configure LDAP you have to provide and bind mount `ldap_config.py` file to `/app/guacozy_server/ldap_config.py`

#### Providing config on windows
Create `ldap_config.py` file in 
`/c/Users/username/dockerdata/guacozy/ldap_config.py`
```
    volumes:
      - /c/Users/username/dockerdata/guacozy/ldap_config.py:/app/guacozy_server/ldap_config.py
```

#### Providing config on linux
Create `ldap_config.py` file in directory `./config/ldap_config.py` (relative to the path where you docker-compose.yml)
```
    volumes:
      - ./config/ldap_config.py:/app/guacozy_server/ldap_config.py
```

#### ldap_config.py.example
You can find ldap_config.py.example on
 [github](https://github.com/paidem/guacozy/blob/master/guacozy_server/guacozy_server/ldap_config.py.example) 
