#!/bin/bash

currdir=$(realpath "$(dirname "$0")")

"$currdir/../genimages.py" \
    < "$currdir/../../res/galleryimages.txt" \
    > "$currdir/../../src/templates/images.html"