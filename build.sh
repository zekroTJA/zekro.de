#!/bin/bash

set -ex

for prescript in scripts/prebuild/*; do
    bash "$prescript"
done

# shellcheck disable=SC2068
./build.py $@