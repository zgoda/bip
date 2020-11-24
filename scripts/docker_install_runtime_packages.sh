#! /bin/bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update

apt-get -y install --no-install-recommends \
	libffi6 libicu63 libmagic1

apt-get clean

rm -rf /var/lib/apt/lists/*
