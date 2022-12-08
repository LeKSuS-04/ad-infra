#!/usr/bin/env bash

# Copy team tokens from vpn server
scp -i "$PRIVATE_KEY_PATH" \
    -o BatchMode=yes \
    -o StrictHostKeychecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o LogLevel=quiet \
    "$USER"@"$HOST":~/ForcAD/tokens/tokens.zip "$TEMP_DIR/team/tokens.zip"

# Extract team token files from archive
cd "$TEMP_DIR/team" || exit
unzip tokens.zip
rm tokens.zip
