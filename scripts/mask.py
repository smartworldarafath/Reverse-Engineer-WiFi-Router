#!/usr/bin/env python3
"""
mask.py - Data sanitizer for Wi-Fi router audit outputs.

Masks sensitive identifiers in logs, tables, and terminal outputs:
- Public IPv4 and IPv6 addresses
- MAC addresses (masks the second half: 00:11:22:XX:XX:XX)
- Hardware serial numbers
- Wi-Fi network names (SSIDs)
- Wi-Fi / admin passwords

Usage:
    python scripts/mask.py < input.log
    cat output.txt | python scripts/mask.py
    python scripts/mask.py input.txt [output.txt]
    python scripts/mask.py --ssid "MyHomeWiFi" < input.txt
"""

import sys
import re
import argparse
import ipaddress

# Matches IPv4 address
IPV4_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

# Matches MAC address (colon or hyphen separated)
MAC_REGEX = re.compile(
    r'\b([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})[:-]([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})\b'
)

# Common serial number patterns (e.g. SN: ABC1234567, SerialNumber: ...)
SERIAL_REGEX = re.compile(
    r'(?i)\b(serial(?:_no|number)?|sn|s/n)[\s:=]+([A-Za-z0-9_-]{6,30})\b'
)

# Password keys in JSON or key-value outputs
PASS_REGEX = re.compile(
    r'(?i)(password|passphrase|wpa_key|psk|secret)[\s:=]+["\']?([^"\'\s,;]+)["\']?'
)


def is_private_ip(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False


def mask_ipv4(match):
    ip_str = match.group(0)
    if is_private_ip(ip_str):
        # Keep local router IPs like 192.168.1.1 or 10.0.0.1 recognizable
        return ip_str
    # Mask public IP
    parts = ip_str.split('.')
    return f"{parts[0]}.{parts[1]}.xxx.xxx"


def mask_mac(match):
    # Keep the first 3 octets (OUI / Manufacturer) and mask the device-specific half
    prefix = match.group(1)
    sep = prefix[2]
    return f"{prefix}{sep}XX{sep}XX{sep}XX"


def mask_serial(match):
    label = match.group(1)
    val = match.group(2)
    masked_val = val[:2] + ("*" * (len(val) - 2))
    return f"{label}: {masked_val}"


def mask_passwords(match):
    key = match.group(1)
    return f"{key}: [REDACTED]"


def sanitize_text(text, custom_ssids=None):
    # 1. Mask passwords
    text = PASS_REGEX.sub(mask_passwords, text)
    
    # 2. Mask serial numbers
    text = SERIAL_REGEX.sub(mask_serial, text)
    
    # 3. Mask MAC addresses (second half)
    text = MAC_REGEX.sub(mask_mac, text)
    
    # 4. Mask public IPs
    text = IPV4_REGEX.sub(mask_ipv4, text)
    
    # 5. Mask custom SSIDs if provided
    if custom_ssids:
        for ssid in custom_ssids:
            if ssid and len(ssid.strip()) > 1:
                text = re.sub(re.escape(ssid.strip()), "[MASKED_SSID]", text, flags=re.IGNORECASE)
                
    return text


def main():
    parser = argparse.ArgumentParser(description="Sanitize diagnostic output by masking sensitive details.")
    parser.add_argument("input_file", nargs="?", help="Input file (defaults to stdin if omitted)")
    parser.add_argument("output_file", nargs="?", help="Output file (defaults to stdout if omitted)")
    parser.add_argument("--ssid", action="append", help="Specific SSID(s) to redact")
    args = parser.parse_args()

    custom_ssids = args.ssid or []

    if args.input_file and args.input_file != "-":
        with open(args.input_file, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    else:
        content = sys.stdin.read()

    sanitized = sanitize_text(content, custom_ssids=custom_ssids)

    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(sanitized)
    else:
        sys.stdout.write(sanitized)


if __name__ == "__main__":
    main()
