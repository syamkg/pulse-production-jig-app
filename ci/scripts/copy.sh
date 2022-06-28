#!/usr/bin/env bash

# This script will copy the required boot scripts for Ansible to provision

set -eu

cp pull.sh rpi/provision/roles/app-launch/files/scripts/
cp run.sh rpi/provision/roles/app-launch/files/scripts/
cp boot.sh rpi/provision/roles/app-launch/files/scripts/
