#!/bin/bash

if git rev-parse --git-dir > /dev/null 2>&1; then
    GIT_REPO_PATH=`git rev-parse --show-toplevel`
    CURR_PATH=$(pwd)
    echo "===== Building the Python package residing at ${GIT_REPO_PATH} ====="
    cd ${GIT_REPO_PATH}
    python -m build  # previously: ./setup.py bdist_wheel
    echo "===== Installing the Python package, may need sudo privilege ====="
    WHEEL_FILE=`ls -t1 dist | head -n 1`
    sudo pip3 install --extra-index https://nexus.winnow.tech/repository/ml-py-repo/simple/ -U dist/${WHEEL_FILE}
    cd ${CURR_PATH}
else
    echo "This is not a git repo. No installation has been performed."
fi
