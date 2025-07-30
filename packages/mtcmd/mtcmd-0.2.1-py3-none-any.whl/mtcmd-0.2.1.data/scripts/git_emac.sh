#!/bin/bash

# git pull the current directory before doing launching emac

if git rev-parse --git-dir > /dev/null 2>&1; then
    git pull
fi

emacs -nw $@

