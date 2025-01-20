#!/bin/bash

currdir=$(realpath "$(dirname "$0")")

python3 "$currdir/../genlist.py" \
    < "$currdir/../../res/gear.yaml" \
    > "$currdir/../../src/templates/gear.html"
