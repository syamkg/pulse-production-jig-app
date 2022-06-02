FROM arm32v7/python:3.9-slim-bullseye

RUN apt-get update --yes && \
    apt-get install --yes \
#        runtime dependencies
        python3-tk \
        zlib1g \
        libtiff5 \
        libopenjp2-7 \
        libjpeg62-turbo \
        fonts-liberation2 && \
     rm -rf /var/lib/apt/lists/*

# add the https://www.piwheels.org/ repo so we don't have to build from source
COPY pip.conf /etc/pip.conf

WORKDIR /usr/src/pulse_jig

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY pulse_jig ./

# We'll set a default value for Dev builds
ARG VERSION=0.0.0
# JIG_ENV is the env_switcher for Dynaconf
ENV JIG_ENV_VERSION=$VERSION
