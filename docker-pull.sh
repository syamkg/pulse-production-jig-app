#!/usr/bin/env bash

set -eu

export AWS_DEFAULT_REGION=ap-southeast-2
export AWS_ACCOUNT_ID=$@

echo "Logging in to $AWS_ACCOUNT_ID's ECR at $AWS_DEFAULT_REGION..."
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com

docker pull $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/pulse-jig:latest

docker tag $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/pulse-jig:latest pulse-jig
docker image ls