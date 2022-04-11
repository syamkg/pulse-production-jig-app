.PHONY: sync check-host check-notifyloop check-rsync test lint

test:
	python -m pytest

lint:
	pre-commit run -a

sync: check-host check-rsync
	rsync -r --exclude=".git" --exclude ".pytest_cache" --exclude ".coverage" --exclude=".venv" --exclude="__pycache__" --exclude="*.pyc" . $(HOST):/home/pi/pulse-dev

watch: check-host check-notifyloop check-rsync
	notifyloop . rsync -avz --exclude=".git" --exclude ".pytest_cache" --exclude ".coverage" --exclude=".venv" --exclude="__pycache__" --exclude="*.pyc" . $(HOST):/home/pi/pulse-dev

check-host:
ifndef HOST
	$(error Environment variable HOST not set.)
endif

check-notifyloop:
ifeq (, $(shell which notifyloop))
	$(error No notifyloop installed.)
endif

check-rsync:
ifeq (, $(shell which rsync))
	$(error No rsync installed.)
endif
