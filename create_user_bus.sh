#!/bin/bash
set -euo pipefail

# Start a temporary user D-Bus session if none is running and output the
# environment variable export so callers can eval the result.
if [ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ]; then
    if dbus-send --session --dest=org.freedesktop.DBus \
        --type=method_call / org.freedesktop.DBus.ListNames >/dev/null 2>&1; then
        echo "export DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS"
        exit 0
    fi
fi

addr=$(dbus-daemon --session --fork --print-address)
echo "export DBUS_SESSION_BUS_ADDRESS=${addr}"
