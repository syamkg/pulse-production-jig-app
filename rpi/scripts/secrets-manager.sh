#!/usr/bin/env bash

set -eu

# Get all instances with the given tag
instances="$( aws ssm describe-instance-information --filters "Key=tag:instance_tag,Values=pulse-jig" )"

# Parse the above output & get the InstanceId
node_id="$( echo $instances | jq -r --arg name "${1}" '.InstanceInformationList | .[] | select( .Name == $name ) | .InstanceId' )"

# Create the secret
aws secretsmanager create-secret \
    --name "${1}" \
    --description "Raspberry Pi login credentials" \
    --secret-string "{\"user\":\"pi\",\"password\":\"${2}\",\"node_name\":\"${1}\",\"node_id\":\"${node_id}\"}"
