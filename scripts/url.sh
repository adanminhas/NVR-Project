#!/usr/bin/env bash
# Print the URLs you can use to reach this Pi NVR instance.
# Use after a fresh install or when you've forgotten the address.
set -euo pipefail

PORT="${PORT:-8000}"

if command -v hostname >/dev/null 2>&1; then
  HOST_NAME="$(hostname)"
  HOST_IP="$(hostname -I 2>/dev/null | awk '{print $1}' || echo unknown)"
else
  HOST_NAME="$(cat /etc/hostname 2>/dev/null || echo "${HOSTNAME:-unknown}")"
  HOST_IP="$(ip -4 -o addr show scope global 2>/dev/null | awk '{print $4}' | head -1 | cut -d/ -f1 || echo unknown)"
fi

printf "%s\n" "http://${HOST_NAME}:${PORT}        (if your router resolves bare hostnames)"
printf "%s\n" "http://${HOST_NAME}.local:${PORT}   (if your devices speak mDNS)"
printf "%s\n" "http://${HOST_IP}:${PORT}    (always works)"
