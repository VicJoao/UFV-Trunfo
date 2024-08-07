#!/bin/bash

# Build the image
docker build -t my-python-app .

# Set up DISPLAY variable for X11 forwarding
export DISPLAY=host.docker.internal:0

# Run the container
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw --rm -it my-python-app
