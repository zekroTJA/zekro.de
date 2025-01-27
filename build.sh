#!/bin/bash

set -ex

for prescript in scripts/prebuild/*; do
    bash "$prescript"
done

temple build --source src --output dist
