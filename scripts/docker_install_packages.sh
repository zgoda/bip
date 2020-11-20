#! /bin/bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt update

apt -y install --no-install-recommends build-essential libffi-dev libicu-dev

apt clean

rm -rf /var/lib/apt/lists/*
