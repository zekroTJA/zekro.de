#!/bin/bash

currdir=$(realpath "$(dirname "$0")")

python3 "$currdir/../genlist.py" \
    < "$currdir/../../res/bike-gear.yaml" \
    > "$currdir/../../src/templates/bike-gear.html"
