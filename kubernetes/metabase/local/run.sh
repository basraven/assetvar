#!/bin/bash
docker volume create metabase
docker run -it --rm --name metabase -e MB_DB_FILE="/metabase-data/metabase.db" -v metabase:/metabase-data -p 33000:3000 metabase/metabase