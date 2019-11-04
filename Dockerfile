ARG BUILDFRONTENDFROM=node:12.2.0-alpine
ARG SERVERFROM=python:3.7-alpine

####################
# BUILDER FRONTEND #
####################

FROM ${BUILDFRONTENDFROM} as builder-frontend
ARG DOCKER_TAG
ADD frontend/package.json /frontend/
ADD frontend/package-lock.json /frontend/
WORKDIR /frontend
RUN npm install
ADD frontend /frontend
ENV REACT_APP_VERSION=$DOCKER_TAG
RUN npm run build

##################
# BUILDER WHEELS #
##################

FROM ${SERVERFROM} as builder-wheels

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update && apk add \
    build-base \
    ca-certificates \
    musl-dev \
    postgresql-dev \
    python3-dev \
    libffi-dev \
    openldap-dev

COPY guacozy_server/requirements*.txt ./
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements-ldap.txt

#########
# FINAL #
#########

FROM ${SERVERFROM}

COPY --from=builder-wheels /usr/src/app/wheels /wheels

# install dependencies
RUN apk update && apk add --no-cache \
      bash \
      libpq \
      ca-certificates \
      openssl \
      memcached \
      nginx \
	  supervisor

# Inject built wheels and install them
COPY --from=builder-wheels /usr/src/app/wheels /wheels
RUN pip install --upgrade pip && \
    pip install --no-cache /wheels/*

# Inject django app
COPY guacozy_server  /app

# Inject built frontend
COPY --from=builder-frontend /frontend/build /frontend

# Inject docker specific configuration
COPY docker /tmp/docker

# Distribute configuration files and prepare dirs for pidfiles
RUN mkdir -p /run/nginx && \
    mkdir -p /run/daphne && \
    cd /tmp/docker && \
    mv entrypoint.sh /entrypoint.sh && \
    chmod +x /entrypoint.sh && \
    mv nginx-default.conf /etc/nginx/conf.d/default.conf && \
    mkdir -p /etc/supervisor.d/ && \
    mv /tmp/docker/supervisor-app.ini /etc/supervisor.d/ && \
    mv /tmp/docker/supervisord.conf /etc/supervisord.conf && \
    # create /app/.env if doesn't exists for less noise from django-environ
    touch /app/.env

ENTRYPOINT ["/entrypoint.sh"]

# Change to app dir so entrypoint.sh can run ./manage.py and other things localy to django
WORKDIR /app

CMD ["supervisord", "-n"]
EXPOSE 80
EXPOSE 443