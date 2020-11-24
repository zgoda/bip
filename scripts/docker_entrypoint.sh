#! /bin/bash

set -euo pipefail

bip db init

gunicorn \
	--preload \
	--workers=2 --threads=4 --worker-class=gthread \
	--log-file - \
	--worker-tmp-dir /dev/shm \
	--bind 0.0.0.0:5000 \
	bip.wsgi:application
