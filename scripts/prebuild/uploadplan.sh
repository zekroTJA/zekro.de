#!/bin/bash

currdir=$(realpath "$(dirname "$0")")

python3 "$currdir/../genuploadplan.py" \
    < "$currdir/../../res/uploadplan.yml" \
    > "$currdir/../../src/templates/uploadplan.html"
