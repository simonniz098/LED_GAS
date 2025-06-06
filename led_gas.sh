#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"
echo "PWD: $(pwd)"

#Required for python venv
source bin/activate

echo "python venv activation return code: $?"
echo "$(which python3)"

./led_gas.py
