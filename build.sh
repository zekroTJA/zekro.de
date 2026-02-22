#!/bin/bash

set -ex

for prescript in scripts/prebuild/*; do
    bash "$prescript"
done

if [[ $SKIP_TEMPLE_BUILD != "1" ]]; then
  temple build --source src --output dist
fi
