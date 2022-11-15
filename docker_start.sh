#!/bin/bash

# NOTE: this is currently in prod on the server.
#       it isnt run by anything inside the project, but
#       should be located at /home/$(whoami)/ :)

# pull latest image
echo -e "\npulling latest image..."
# docker pull OMITTED

# if exists, stop the running server
if docker ps | grep canvas2 > /dev/null; then
    echo -e "\nstopping old server..."
    docker stop canvas2
    docker rm canvas2
fi

# start new updated server
echo -e "\nstarting new server..."
# docker run -d --name canvas2 --restart unless-stopped --env-file="/home/$(whoami)/.flaskenv.prod" -p 5000:5000 OMITTED
