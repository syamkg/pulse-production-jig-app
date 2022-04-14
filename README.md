# pulse-production-jig-app

A python3 GUI application that runs on an RPi and flashes, configures, tests and registers Pulse r1b and probes.

## Setup

After a fresh clone run:

```bash
pip install -r requirements.txt
pre-commit install
```

## Testing

Tests are implemented with pytest. Run them with:

```bash
python -m pytest 
```

## Formating

Formatting is done via [Black](https://github.com/psf/black). It's opinionated and not very configurable so just accept
its formatting and don't fight it :)

To format on commit, install the pre-commit git hook upon a fresh clone of the repository:

```bash
pre-commit install
```

## Running in local

```shell
cd pulse_jig
python app.py
```

## Running in docker

### BUILD (optional)

```bash
docker buildx build --platform linux/arm/v7 -t pulse-jig .
```

### PULL FROM ECR (not required if building)

```shell
./docker-pull <AWS_ACCOUNT_ID>
```

### RUN

```shell
./run.sh python app.py
```

## Settings

This application uses [Dynaconf](https://www.dynaconf.com/) to maintain settings. All settings can be overwritten via ENVs at runtime. The following files are used:

- `settings.yml`, used for settings that don't change between environments but we may wish to configure in special circumstances.
- `settings.local.yaml`, used for environment specific settings. These are not committed to a repository.
- `settings.dev.yaml`, an example `settings.local.yaml` file for development purposes.

Validation is performed on the combined resolved settings in `config.py`. It can be used to access settings in this way:

```python
from config import settings
print(f"join eui: {settings.lora.join_eui}")
```