#!/bin/bash
set -e

# wait shortly and then run db migrations (retry on error)
while ! python ./manage.py migrate 2>&1; do
  echo "Waiting on DB..."
  sleep 3
done

# create superuser silently
if [ -z ${SUPERUSER_NAME+x} ]; then
  SUPERUSER_NAME='admin'
fi
if [ -z ${SUPERUSER_EMAIL+x} ]; then
  SUPERUSER_EMAIL='admin@example.com'
fi
if [ -z ${SUPERUSER_PASSWORD+x} ]; then
    SUPERUSER_PASSWORD='admin'
fi

echo "Username: ${SUPERUSER_NAME}, E-Mail: ${SUPERUSER_EMAIL}"

python ./manage.py shell --interface python << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${SUPERUSER_NAME}'):
    u=User.objects.create_superuser('${SUPERUSER_NAME}', '${SUPERUSER_EMAIL}', '${SUPERUSER_PASSWORD}')
END

# copy static files
python ./manage.py collectstatic --no-input

# init default groups
python ./manage.py initgroups
python ./manage.py initguacd

# Nginx
# if certificates doesn't exist create a self signed certificate
[ ! -f /etc/ssl/private/nginx.key ] && \
[ ! -f /etc/ssl/certs/nginx.crt ] && \
echo "/etc/ssl/private/nginx.key and /etc/ssl/certs/nginx.crt not provided" && \
echo "Creating self signed certificate:" && \
openssl req -x509 -nodes -days 3650 -subj "/CN=guacozy" -addext "subjectAltName=DNS:guacozy" -newkey rsa:4096 -keyout /etc/ssl/private/nginx.key -out /etc/ssl/certs/nginx.crt;


echo "Initialisation is done."

# launch whatever is passed by docker
# (i.e. the RUN instruction in the Dockerfile)
exec ${@}