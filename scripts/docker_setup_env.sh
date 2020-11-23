#! /bin/bash

set -euo pipefail

export DATADIR=/home/bip/data

mkdir -p "$DATADIR/config"
mkdir -p "$DATADIR/attachments"

ln -s /home/bip/.local/lib/python3.8/site-packages/bip/static "$DATADIR/static"
