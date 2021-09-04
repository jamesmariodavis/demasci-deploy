#!/bin/bash

mkdir /coin-or
# first argument passed to script determines if CBC should be installed
if [ "$1" = "y" ]; then
    git clone https://www.github.com/coin-or/coinbrew &&\
    chmod u+x coinbrew/coinbrew &&\
    ./coinbrew/coinbrew build Cbc \
    --prefix=/coin-or \
    --no-prompt \
    --latest-release \
    --static ADD_FFLAGS=-fallow-argument-mismatch
fi