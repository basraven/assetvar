#!/bin/bash
# -v $PWD/data:/var/lib/postgresql/data
docker volume create timescaledb
docker run -it --rm --name timescaledb -v timescale:/var/lib/postgresql/data -p 5432:5432 -e POSTGRES_PASSWORD=password timescale/timescaledb:2.1.1-pg13