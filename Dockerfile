FROM arm32v7/python:3-slim

RUN apt-get update --yes && \
  apt-get install --yes \
    # runtime dependency
    python3-tk \
    zlib1g \
    libtiff5 \
    libopenjp2-7 \
    libjpeg62-turbo && \
    # build dependencies [if not using piwheels...]
    # libffi-dev \
    # libfreetype6-dev \
    # libfribidi-dev \
    # libharfbuzz-dev \
    # libimagequant-dev \
    # libjpeg-turbo-progs \
    # liblcms2-dev \
    # libopenjp2-7-dev \
    # libtiff5-dev \
    # libwebp-dev \
    # netpbm \
    # python3-dev \
    # python3-numpy \
    # python3-scipy \
    # python3-setuptools \
    # tcl8.6-dev \
    # tk8.6-dev \
    # zlib1g-dev && \
  rm -rf /var/lib/apt/lists/*

# add the https://www.piwheels.org/ repo so we don't have to build from source 
COPY pip.conf /etc/pip.conf

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]
