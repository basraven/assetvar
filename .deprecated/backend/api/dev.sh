#!/bin/bash
# python3 -m venv venv # to make new venv
# source venv/bin/activate # to activate venv
docker run -it --rm --name api -v $PWD:/backend -p 5000:5000 -w /backend python:3 bash -c "source venv/bin/activate && flask run"