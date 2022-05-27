#!/usr/bin/env bash

# This script will copy the required boot scripts for Ansible to provision

set -eu

cp pull.sh rpi/provision/roles/app-launch/files/scripts/
cp run.sh rpi/provision/roles/app-launch/files/scripts/
cp boot.sh rpi/provision/roles/app-launch/files/scripts/
cp app.env.example rpi/provision/roles/app-launch/files/settings/app.env
cp settings.yaml rpi/provision/roles/app-launch/files/settings/
touch rpi/provision/roles/app-launch/files/settings/settings.local.yaml