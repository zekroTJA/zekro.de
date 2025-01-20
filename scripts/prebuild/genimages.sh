#!/bin/bash

currdir=$(realpath "$(dirname "$0")")

python3 "$currdir/../genimages.py" \
    < "$currdir/../../res/galleryimages.txt" \
    > "$currdir/../../src/templates/images.html"