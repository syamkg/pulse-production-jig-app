#!/usr/bin/env bash

set -eu

#####################################################################################
# Your CodeBuild job runs with the bare minimum permissions.
# In order to deploy resources, it will need to assume a deployment role.
# Running this script before deployment will achieve that.
#####################################################################################

# Assume role script - calls sts and exports temp creds as env vars
unset AWS_CREDENTIAL_EXPIRATION
unset AWS_SESSION_TOKEN
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_REGION
# unset AWS_PROFILE
ROLE_ARN=$CNF_WORKLOAD_DEPLOYMENT_ROLE_ARN
ROLE_SESSION_NAME=$(echo $CNF_CODEBUILD_PROJECT | cut -c -64)
response=$(aws sts assume-role --role-arn $ROLE_ARN  --role-session-name $ROLE_SESSION_NAME --duration-seconds 900)
# echo $response
unset access_key
access_key=$(echo $response | jq -r '.Credentials.AccessKeyId')
# echo "Access_key is: " $access_key
export AWS_ACCESS_KEY_ID=$access_key
unset secret_access_key
secret_access_key=$(echo $response | jq -r '.Credentials.SecretAccessKey')
# echo "Secret access key is: " $secret_access_key
export AWS_SECRET_ACCESS_KEY=$secret_access_key
unset session_token
session_token=$(echo $response | jq -r '.Credentials.SessionToken')
# echo "Session token is: " $session_token
export AWS_SESSION_TOKEN=$session_token
unset expiration
expiration=$(echo $response | jq -r '.Credentials.Expiration')
# echo "Expiration is: " $expiration
export AWS_CREDENTIAL_EXPIRATION=$expiration
export AWS_REGION=ap-southeast-2
# export AWS_PROFILE=default