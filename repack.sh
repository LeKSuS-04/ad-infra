#!/bin/bash

set -ex

if [ -z "$PASSWORD" ]; then
    echo "You must provide \$PASSWORD env variable";
    exit 1;
fi

zips=$(find ./generated/ -name '*.zip');
pwd=$(pwd)

for generated_path in $zips; do
    filename=$(basename "$generated_path")
    echo "Repacking $filename"

    tmpdir=$(mktemp -d)
    7z x -p"$PASSWORD" -o"$tmpdir" "$generated_path"
    cd "$tmpdir"
    zip -P "$PASSWORD" -r "$filename" "$(ls)"
    mv "$filename" "$pwd/$generated_path"

    cd "$pwd"
done
