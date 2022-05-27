.PHONY: sync check-host check-notifyloop check-rsync test lint

env ?= app.env
-include $(env)
export $(-shell sed 's/=.*//' $(env))

pull: guard-AWS_ACCOUNT_ID
	AWS_ACCOUNT_ID=$(AWS_ACCOUNT_ID) ./pull.sh

build:
	docker buildx build --platform linux/arm/v7 -t pulse-jig .

run: guard-APP_DIR
	APP_DIR=$(APP_DIR) ./run.sh python app.py -t $(TARGET)

run-shell: guard-APP_DIR
	APP_DIR=$(APP_DIR) ./run.sh bash

test:
	python -m pytest

lint:
	pre-commit run -a

sync: guard-HOST check-rsync
	rsync -r --exclude=".git" --exclude ".pytest_cache" --exclude ".coverage" --exclude=".venv" --exclude="__pycache__" --exclude="*.pyc" . $(HOST):$(APP_DIR)

watch: guard-HOST check-notifyloop check-rsync
	notifyloop . rsync -avz --exclude=".git" --exclude ".pytest_cache" --exclude ".coverage" --exclude=".venv" --exclude="__pycache__" --exclude="*.pyc" . $(HOST):$(APP_DIR)

check-notifyloop:
ifeq (, $(shell which notifyloop))
	$(error No notifyloop installed.)
endif

check-rsync:
ifeq (, $(shell which rsync))
	$(error No rsync installed.)
endif

guard-%:
	@ if [ "${${*}}" = "" ]; then \
	    echo "Environment variable $* not set"; \
	    exit 1; \
	fi