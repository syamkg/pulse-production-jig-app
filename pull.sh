#!/usr/bin/env bash

set -eu

if [[ -z "${AWS_ACCOUNT_ID}" ]]; then
  echo "AWS_ACCOUNT_ID is not set!"
  exit
fi

AWS_REGION=ap-southeast-2

echo "Logging in to ${AWS_ACCOUNT_ID}'s ECR at ${AWS_REGION}..."
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com

docker pull "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com/pulse-jig:latest

docker tag "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com/pulse-jig:latest pulse-jig
docker image ls