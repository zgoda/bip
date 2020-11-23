#! /bin/bash

set -euo pipefail

pip install --user -U --no-cache-dir --no-warn-script-location pip wheel setuptools Cython

pip install --user -U --no-cache-dir --no-warn-script-location .

pip install --user -U --no-cache-dir --no-warn-script-location gunicorn
