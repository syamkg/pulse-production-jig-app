#!/usr/bin/env bash

set -eu

echo Fetching the tagged version...

git_tag=$(git for-each-ref refs/tags --sort=-creatordate --count=1 --format=%\(refname:short\))

if [ -z "$git_tag" ]
then
  echo "No GIT tags found."
else
  echo "Latest GIT tag: ${git_tag}"
fi

export VERSION=${git_tag#*v}
