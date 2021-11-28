#!/bin/bash
# python3 -m venv venv # to make new venv
# source venv/bin/activate # to activate venv
docker run -it --rm --name worker -v $PWD:/backend -w /backend python:3 bash # -c "source venv/bin/activate && flask run"