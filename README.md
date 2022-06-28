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

## Formatting

Formatting is done via [Black](https://github.com/psf/black). It's opinionated and not very configurable so just accept
its formatting and don't fight it :)

To format on commit, install the pre-commit git hook upon a fresh clone of the repository:

```bash
pre-commit install
```

## Tagging and versioning

A GitHub Action has set up on `deploy.yaml` to automatically tag when merging to `main`. This will follow the standard 
semantic versioning with prefix `v`

By default, this will increment the `patch` version number. To override this default behavior, 
include `#major`, `#minor` or `#patch` tags in the commit message. 

Extra reading: https://github.com/anothrNick/github-tag-action

## Running in local

```shell
cd pulse_jig
python app.py -t <TARGET>
```

Add `DISPLAY=:0` if running via SSH
```shell
DISPLAY=:0 python app.py -t <TARGET>
```

## Running in docker

### Option 1: Build

```bash
make build
```

### Option 2: Pull from ECR

```shell
make pull 
```

### Run

```shell
make run
```

Add `DISPLAY=:0` if running via SSH
```shell
DISPLAY=:0 make run
```

## Settings

This application uses [Dynaconf](https://www.dynaconf.com/) to maintain settings. All settings can be overwritten via ENVs at runtime. The following files are used:

- `settings.yml`, used for settings that don't change between environments but we may wish to configure in special circumstances.
- `settings.local.yaml`, used for environment specific settings. These are not committed to a repository.
- `settings.dev.yaml`, used for local development work, copy to `settings.local.yaml` to get running locally quickly.

Validation is performed on the combined resolved settings in `config.py`. It can be used to access settings in this way:

```python
from pulse_jig.config import settings
print(f"join eui: {settings.lora.join_eui}")
```

## Environment variables
`app.env` file contains the environment specific values required until app starts. This is separate to above-mentioned
`settings.yaml` - which has the settings required during the run-time.

Copy the contents from `app.env.dev` to set up a dev environment.

## App auto launch config 
- A `.desktop` entry will be created in `/etc/xdg/autostart/jig-app.desktop` to auto launch the Jig App.
- This entry will then fire `boot.sh`.
- A `zenity` progress bar added to factory worker to indicate app is launching (which will takes about 10 seconds)

## Deploying boot scripts
If you running Ansible on your local to provision any jig it's important to run following before Ansible
```shell
. ./ci/scripts/copy.sh
```
This will copy the boot scripts to the relevant Ansible role.

`deploy.buildspec.yaml` will also run the above before zipping the Ansible playbooks, so that they are available for Systems Manager provisioning. 
