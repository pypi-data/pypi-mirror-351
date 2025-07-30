#!/bin/bash

# git commit, then git pull, then git push

git commit -am "${1}"
git pull
git push
