#!/usr/bin/env bash

# Ensure that all dependencies exist
dependencies="jq zip unzip"
for dep in $dependencies; do
    if ! command -v "$dep" &>/dev/null; then
        echo "\"$dep\" must be available in \$PATH to continue"
        exit 1
    fi
done

# Ensure directory with services and checkers exists
if [ ! -d "$SRC_DIR" ]; then
    echo "Directory with checkers and services ($SRC_DIR) does not exist"
    exit 1
else
    if [ ! -d "$SRC_DIR/checkers" ]; then
        echo "Directory with checkers ($SRC_DIR/checkers) does not exist"
    fi

    if [ ! -d "$SRC_DIR/services" ]; then
        echo "Directory with services ($SRC_DIR/services) does not exist"
    fi
fi

# Create temporary directory and result directory
mkdir -p "$RESULT_DIR"
mkdir -p "$TEMP_DIR"

# Ensure those directories is empty
rm -rf "${RESULT_DIR:?}"/*
rm -rf "${TEMP_DIR:?}"/*

# Pack checkers and services to archives
cd "$SRC_DIR/checkers" || exit
zip -r checkers.zip ./*
cd "$SRC_DIR/services" || exit
zip -r services.zip ./*
mv "$SRC_DIR/checkers/checkers.zip" "$TEMP_DIR/checkers.zip"
mv "$SRC_DIR/services/services.zip" "$TEMP_DIR/services.zip"

