ARG PYTHON_VERSION=3.9-slim-buster


# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# python build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=local

# install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev \
  # other
  apt-utils

# requirements are installed here to ensure they will be cached.
COPY ./requirements .

# create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels -r ${BUILD_ENVIRONMENT}.txt


# python 'run' stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app
ARG SUBLIST3R_VERSION=1.1

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # openssh-client
  openssh-client \
  # openssh-server
  openssh-server \
  # ca-certificates
  ca-certificates \
  # lxml
  libxml2-dev \
  libxslt-dev \
  # gevent
  libev-dev \
  libuv1-dev \
  libevent-dev \
  # xsltproc
  xsltproc \
  # libcurl3
  libcurl3-openssl-dev \
  # sublist3r
  python-requests \
  python-dnspython \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* && rm -rf /wheels/

# install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y git

# start commands
COPY ./compose/local/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# celery workers
COPY ./compose/local/django/celery/worker/_main /start-celeryworker-main
RUN sed -i 's/\r$//g' /start-celeryworker-main
RUN chmod +x /start-celeryworker-main

# celery beat
COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

# celery flower
COPY ./compose/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

# copy application code to WORKDIR
COPY . ${APP_HOME}


ENTRYPOINT ["/entrypoint"]
