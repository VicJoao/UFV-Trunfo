#!/bin/bash

# Build the image
sudo docker build -t my-python-app .

# Allow connections through X11
xhost +local:docker

# Run the container
sudo docker run -u=$(id -u):$(id -g) -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw --rm -it my-python-app
