#!/usr/bin/env bash

# This will pull,
#   1. Functional tests firmware
#   2. Production firmware
#   3. Troubleshoot firmware
# from the OTA bucket in wpl-wrk-ias-prd account

set -eu

script_path=$(realpath "$0")
dir_path=$( dirname "${script_path}" )
cd "${dir_path}"

aws s3 cp s3://ias-iot-ota-firmware/bin/PulseR1B/pulse-functional-tests.bin ../../pulse_jig/firmware/test-firmware.bin
aws s3 cp s3://ias-iot-ota-firmware/bin/PulseR1B/pulse-production.bin ../../pulse_jig/firmware/prod-firmware.bin
aws s3 cp s3://ias-iot-ota-firmware/bin/PulseR1B/troubleshoot.bin ../../pulse_jig/firmware/troubleshoot.bin
