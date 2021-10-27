

# Setup

After a fresh clone run:

```bash
pip install -r requirements.txt
pre-commit install
```

# Testing

Tests are implemented with pytest. Run them with:

```bash
python -m pytest 
```

# Formating

Formatting is done via [Black](https://github.com/psf/black). It's opinionated and not very configurable so just 
accept its formatting and don't fight it :)

To format on commit, install the pre-commit git hook upon a fresh clone of the repository:

```bash
pre-commit install
```

# Running in docker

```bash
docker buildx build --platform linux/arm/v7 -t pulse-jig .
docker run --platform linux/arm/v7 -it -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -u $(id -u ${USER}):$(id -g ${USER}) pulse-jig
```

