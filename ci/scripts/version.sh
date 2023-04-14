#!/usr/bin/env bash

set -eu

echo Fetching the tagged version...

git_tag=$(cat PROJECT_VERSION.txt)

if [ -z "$git_tag" ]
then
  echo "No GIT tags found."
else
  echo "Latest GIT tag: ${git_tag}"
fi

export VERSION=${git_tag#*v}
