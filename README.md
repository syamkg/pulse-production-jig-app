

Running:

```bash
docker buildx build --platform linux/arm/v7 -t pulse-jig .
docker run --platform linux/arm/v7 -it -e DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -u $(id -u ${USER}):$(id -g ${USER}) pulse-jig
```

