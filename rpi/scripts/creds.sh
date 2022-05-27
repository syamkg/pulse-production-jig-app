#!/usr/bin/env bash

# This script will retrieve the Password & SSM Node ID for a given
# Raspberry Pi by SSM Node Name & save them as env vars.
#
# Example usage:
#   source ./creds.sh intellisense-jig-1-1
#   echo $JIG_PASSWORD | pbcopy
#   ssh pi@$JIG_NODE_ID
#   ansible-playbook -i $JIG_NODE_ID, -u pi maintenance.yml -k

set -eu

details="$( aws secretsmanager get-secret-value --secret-id "${1}" --query SecretString --output text )"

export JIG_PASSWORD="$( echo $details | jq -r .password)"
export JIG_NODE_ID="$( echo $details | jq -r .node_id)"
