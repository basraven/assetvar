#!/bin/bash
docker run -it -v $PWD:/src -e APITOKEN=$APITOKEN -w /src python:3.8 bash