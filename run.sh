#!/usr/bin/env bash

set -u

source app.env

if [[ -z "${APP_DIR}" ]]; then
  echo "APP_DIR is not set!"
  exit
fi

tty=""
if [[ "$1" == "bash" ]]; then
  tty="t"
fi

xhost +local:

/usr/bin/docker run -i"${tty}" --rm \
  --platform linux/arm/v7 \
  --env DISPLAY \
  --env QT_X11_NO_MITSHM=1 \
  --volume /tmp/.X11-unix:/tmp/.X11-unix \
  --volume /media/pi/XDOT/:/media/pi/XDOT \
  --volume /home/pi/.aws:/root/.aws \
  --volume "${APP_DIR}"/settings.yaml:/usr/src/pulse_jig/settings.yaml \
  --volume "${APP_DIR}"/settings.local.yaml:/usr/src/pulse_jig/settings.local.yaml \
  --volume "${APP_DIR}"/pulse_jig/firmware:/usr/src/pulse_jig/firmware \
  --privileged \
  pulse-jig "$@"

xhost -local: