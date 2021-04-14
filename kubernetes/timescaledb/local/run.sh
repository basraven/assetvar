#!/bin/bash
# -v $PWD/data:/var/lib/postgresql/data
docker run -it --rm --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=password timescale/timescaledb:2.1.1-pg13