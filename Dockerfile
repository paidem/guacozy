ARG BUILDFRONTENDFROM=node:12.2.0-alpine
ARG SERVERFROM=python:3.7-alpine

####################
# BUILDER FRONTEND #
####################

FROM ${BUILDFRONTENDFROM} as builder-frontend
ADD frontend/package.json /frontend/
ADD frontend/package-lock.json /frontend/
WORKDIR /frontend
RUN npm install
ADD frontend /frontend
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
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements-ldap.txt

#########
# FINAL #
#########

FROM ${SERVERFROM}

COPY --from=builder-wheels /usr/src/app/wheels /wheels

# install dependencies
RUN apk update && apk add --no-cache \
      bash \
      libpq \
      ca-certificates

COPY --from=builder-wheels /usr/src/app/wheels /wheels
RUN pip install --no-cache /wheels/*

# create the home directory
ENV APP_HOME=/app

# create the app user
# create directory for the static files and all other in the path
# we need to create staticfiles dir in advance and chown, because permissions later on volume will not let us
RUN addgroup -S app && \
    adduser -S app -G app && \
    mkdir -p $APP_HOME/staticfiles && \
    touch $APP_HOME/.env && \
    chown -R app:app $APP_HOME

WORKDIR $APP_HOME

# change to the app user
USER app

# copy project and chown all the files to the app user
COPY --chown=app:app guacozy_server $APP_HOME

# make entrypoint executable
RUN chmod +x $APP_HOME/entrypoint.sh

# copy built fronend to static folder, so it can be collected by collectstatic on start
# after "manape.py collectstatic" will be run, it will be copied to $APP_HOME/staticfiles/cozy
COPY --chown=app:app --from=builder-frontend /frontend/build $APP_HOME/static/cozy

# Specify entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["daphne", "-b", "0.0.0.0","-p","8001","guacozy_server.asgi:application"]
EXPOSE 8001