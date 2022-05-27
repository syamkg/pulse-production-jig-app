#!/usr/bin/env bash

aws secretsmanager create-secret \
    --name "$1" \
    --description "Raspberry Pi login credentials" \
    --secret-string "{\"user\":\"pi\",\"password\":\"$2\",\"node_name\":\"$1\"}"