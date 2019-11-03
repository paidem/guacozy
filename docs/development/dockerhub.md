Docker images are hosted at https://hub.docker.com/r/guacozy/guacozy-server

gucacozy-server DockerHub repository has automatic builds configured, which monitors commits tagged `
/^[0-9.]+/` (starts with number) and builds version with `v` prefix (e.g. tag commit `0.0.15`, image will be built with `v0.0.15` tag)

Every image built this way is added `latest` tag (using `post_push` hook in `/hooks/` folder)