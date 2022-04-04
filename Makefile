.PHONY: sync check-host

sync: check-host
	rsync -r --exclude=".git" --exclude ".pytest_cache" --exclude ".coverage" --exclude=".venv" --exclude="__pycache__" --exclude="*.pyc" . $(HOST):/home/pi/pulse-dev

watch: check-host
	notifyloop . rsync -avz --exclude=".git" --exclude ".pytest_cache" --exclude ".coverage" --exclude=".venv" --exclude="__pycache__" --exclude="*.pyc" . $(HOST):/home/pi/pulse-dev

check-host:
ifndef HOST
	$(error Environment variable HOST not set)
endif
