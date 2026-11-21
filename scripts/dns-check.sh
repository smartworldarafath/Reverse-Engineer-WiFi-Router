#!/usr/bin/env bash
#
# dns-check.sh - Check which provider answers your DNS lookups
#
# Usage:
#   ./scripts/dns-check.sh
#

set -e

echo "=== DNS Resolution Provider Check ==="
echo ""

# 1. Check local resolver IP from system configuration
echo "[1/3] System DNS Resolver:"
if [ -f /etc/resolv.conf ]; then
    grep "nameserver" /etc/resolv.conf | awk '{print "  -> " $2}'
elif command -v scutil >/dev/null 2>&1; then
    scutil --dns | grep "nameserver\[0\]" | awk '{print "  -> " $3}' | sort -u
elif command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe -NoProfile -Command "Get-DnsClientServerAddress -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses" | while read -r line; do
        [ -n "$line" ] && echo "  -> $line"
    done
else
    echo "  -> Could not determine system resolver."
fi
echo ""

# 2. Perform test query to detect external resolver identity
echo "[2/3] Querying DNS Resolver Identity..."
RESOLVER_IP=""

# Try Cloudflare whoami
if command -v dig >/dev/null 2>&1; then
    RESOLVER_IP=$(dig +short @1.1.1.1 whoami.cloudflare ch txt 2>/dev/null | tr -d '"')
elif command -v nslookup >/dev/null 2>&1; then
    RESOLVER_IP=$(nslookup -type=txt whoami.cloudflare 1.1.1.1 2>/dev/null | grep -i "text =" | awk -F'=' '{print $2}' | tr -d ' "\r\n')
fi

# Fallback: check whoami.akamai.net
if [ -z "$RESOLVER_IP" ]; then
    if command -v dig >/dev/null 2>&1; then
        RESOLVER_IP=$(dig +short whoami.akamai.net 2>/dev/null)
    elif command -v nslookup >/dev/null 2>&1; then
        RESOLVER_IP=$(nslookup whoami.akamai.net 2>/dev/null | grep -A1 "Name:" | grep "Address:" | awk '{print $2}' | tr -d '\r\n')
    fi
fi

if [ -n "$RESOLVER_IP" ]; then
    echo "  -> Outgoing DNS Resolver IP: $RESOLVER_IP"
else
    echo "  -> Could not retrieve outgoing resolver IP."
fi
echo ""

# 3. Lookup ASN / Organization of resolver
echo "[3/3] Resolver Organization / ISP:"
if [ -n "$RESOLVER_IP" ]; then
    ORG=$(curl -s --max-time 5 "https://ipinfo.io/${RESOLVER_IP}/org" 2>/dev/null || true)
    if [ -n "$ORG" ]; then
        echo "  -> Organization: $ORG"
    else
        echo "  -> Lookup failed or connection timed out."
    fi
else
    echo "  -> Skipped (no resolver IP identified)."
fi

echo ""
echo "=== Check Complete ==="
echo "Note: If Organization shows your local ISP, your queries are exposed in plain text."
echo "If Organization shows Cloudflare, Google, Quad9, or NextDNS, DNS encryption is active."
