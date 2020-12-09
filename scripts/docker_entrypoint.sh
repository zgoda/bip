#! /bin/bash

set -euo pipefail

rm -rf /home/bip/data/static
ln -s /home/bip/venv/lib/python3.8/site-packages/bip/static /home/bip/data/static

/home/bip/venv/bin/bip db init

/home/bip/venv/bin/gunicorn \
	--name bip \
	--preload \
	--workers=2 --threads=4 --worker-class=gthread \
	--log-file=- \
	--worker-tmp-dir /dev/shm \
	--bind unix:/home/bip/run/gunicorn.sock \
	bip.wsgi:application
