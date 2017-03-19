#!/usr/bin/env bash

# exit if any command returns a non-zero status
set -e

# This script is meant to be run inside the
# docker development environment

if [ $# -lt 1 ]; then
    help
    exit 1
fi

function help() {
    echo "USAGE:"
    echo "    start: Start the jupyter notebook"
    echo ""
}

function start() {
    export PATH=/work/micropython/unix:$PATH
    jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser &
}

case "$1" in
    'start'):
        start
        ;;
    *):
        help
        ;;
esac

