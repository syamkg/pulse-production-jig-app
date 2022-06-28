#!/usr/bin/env bash

set -eu

source app.env

if [[ -z "${APP_DIR}" ]]; then
  echo "APP_DIR is not set!"
  exit
fi

tty=""
if [[ "$1" == "bash" ]]; then
  tty="t"
fi

# If XDOT programmer is already mounted we'll unmount it first
mount_point=$( lsblk -fp | awk '/XDOT/ {print $8}' )
if [ -n "${mount_point}" ]; then
  gio mount -u "${mount_point}"
fi

# Remove any junk mount points before attempting re-mount
sudo rm -rf /media/pi/XDOT*

# Then mount the XDOT programmer
device=$( lsblk -fp | awk '/XDOT/ {print $1}' )
gio mount -d "${device}"
mount_point=$( lsblk -fp | awk '/XDOT/ {print $8}' )

# Turn-off exit on error as from here onwards we want to make sure
# `xhost -local` get fired regardless
set +e

# Grant access to X from the local network
xhost +local:

# Run docker
/usr/bin/docker run -i"${tty}" --rm \
  --platform linux/arm/v7 \
  --env DISPLAY \
  --env QT_X11_NO_MITSHM=1 \
  --volume /tmp/.X11-unix:/tmp/.X11-unix \
  --volume "${mount_point}":/media/pi/XDOT \
  --volume /home/pi/.aws:/root/.aws \
  --volume "${APP_DIR}"/settings.yaml:/usr/src/pulse_jig/settings.yaml \
  --volume "${APP_DIR}"/settings.local.yaml:/usr/src/pulse_jig/settings.local.yaml \
  --volume "${APP_DIR}"/pulse_jig/firmware:/usr/src/pulse_jig/firmware \
  --privileged \
  pulse-jig "$@"

# Revoke access to X from the local network
xhost -local:
