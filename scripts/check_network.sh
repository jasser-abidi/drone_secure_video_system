#!/bin/bash
echo "=== Active connections ==="
nmcli connection show --active
echo ""
echo "=== Routes ==="
ip route
echo ""
echo "=== Tailscale status ==="
tailscale status
