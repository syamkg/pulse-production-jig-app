#!/usr/bin/env bash

set -u

xhost +local:

docker run -it --rm \
  --platform linux/arm/v7 \
  --env DISPLAY \
  --env QT_X11_NO_MITSHM=1 \
  --volume /tmp/.X11-unix:/tmp/.X11-unix \
  --volume /media/pi/XDOT/:/media/pi/XDOT \
  --volume /home/pi/Desktop/test-jig/pulse_jig/firmware:/usr/src/app/firmware \
  --privileged \
  pulse-jig $@

xhost -local: