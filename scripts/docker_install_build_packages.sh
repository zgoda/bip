#! /bin/bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update

apt-get -y install --no-install-recommends \
	build-essential libffi-dev libicu-dev libmagic-dev

apt-get clean

rm -rf /var/lib/apt/lists/*
