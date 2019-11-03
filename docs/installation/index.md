The easiest way to run Guacozy is using [_docker-compose_](docker-compose.md), which will provide 2 additional containers:
  
- _PostgreSQL database_ - needed to store connection data, users, etc.
- _guacd_ - needed to make actual VNC/RDP/SSH connections


If you already use Apache Guacamole, you can run it as a single docker container, which will use SQLite database and specify your guacd in application settings after it starts.


