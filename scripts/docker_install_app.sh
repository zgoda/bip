#! /bin/bash

set -euo pipefail

pip install --user -U --no-cache-dir --no-warn-script-location -e .

pip install --user -U --no-cache-dir --no-warn-script-location gunicorn
