#!/bin/bash -ex

docker rmi maxzheng/console-games
docker build . -t maxzheng/console-games
docker push maxzheng/console-games
