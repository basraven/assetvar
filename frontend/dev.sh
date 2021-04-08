#!/bin/bash
# npx create-react-app assetvar
docker run -it --rm --name frontend -p 3000:3000 -v $PWD:/frontend -w /frontend  -u node node bash