---
name: reverse-engineer-wifi-router
description: Reverse-engineer your home Wi-Fi router's admin API using a photo of the router to perform privacy audits or optimize/fix slow Wi-Fi.
version: 1.0.0
---

# Reverse-Engineer Wi-Fi Router

Reverse-engineer a home Wi-Fi router's administration interface using a single photo of the router. This skill works out the router's web API and performs either a privacy audit or slow Wi-Fi diagnostics and resolution.

## Core Rules & Safety Guardrails

- **Local Network Only**: Strictly operate on the user's currently connected local subnet (e.g. `192.168.1.0/24`, `192.168.0.0/24`). Never execute scans, connections, or packets targeting public external IPs or WAN addresses.
- **No Exploits / No Password Guessing**: Do not perform brute-force dictionary attacks or exploit known CVEs. Use legitimate local HTTP/HTTPS/JSON/CGI admin endpoints.
- **Zero Chat Credential Leakage**:
  - NEVER ask the user to type router credentials or passwords into the chat.
  - NEVER print plaintext passwords or credentials in the chat output.
  - Always generate a local system command to store and retrieve the router admin password securely using native system keystores:
    - **macOS**: `security add-generic-password -s "wifi-router-admin" -a "admin" -w "<password>"` and `security find-generic-password -s "wifi-router-admin" -w`
    - **Linux**: `secret-tool store --label="wifi-router-admin" service wifi-router-admin username admin` and `secret-tool lookup service wifi-router-admin username admin`
    - **Windows**: Use Windows Credential Manager or DPAPI via PowerShell (`cmdkey /generic:wifi-router-admin /user:admin /pass:...`).
- **Data Masking**: Always sanitize output before displaying it. Run or apply `scripts/mask.py` to mask public IP addresses, the second half of MAC addresses (`XX:XX:XX:__:__:__`), hardware serial numbers, and Wi-Fi SSIDs.
- **User Confirmation Required for Changes**:
  - Job 1 (Privacy Check) is strictly **READ-ONLY**.
  - Job 2 (Fix Slow Wi-Fi) requires explicit user confirmation before applying any setting change or reboot.

---

## Workflow 1: Privacy Check (Read-Only)

Triggered by questions like:
- *"What does my router know about me?"*
- *"Audit my router privacy"*
- *"Check what my ISP can see"*

### Step 1: Device Identification
1. Ask the user for a photo of the physical router (instructing them to cover any Wi-Fi password stickers).
2. Identify brand, model number, hardware revision, FCC ID, and default gateway IP (typically `192.168.1.1` or `192.168.0.1`).
3. If an app-only system (e.g. eero, Google Nest) is detected without a web interface, provide a curated network-level inspection summary.

### Step 2: Gateway Discovery & Authentication Setup
1. Identify the default gateway IP using `ip route`, `netstat -rn`, or `ipconfig`.
2. Probe local web endpoints (`/`, `/login.html`, `/api/`, `/cgi-bin/`) to discover API structure (REST JSON endpoints, CGI forms, or LuCI/OpenWrt RPC).
3. If credentials are required, provide the one-line system keystore command so the password is saved locally and retrieved via environment variable or script.

### Step 3: Read-Only Data Extraction
Collect the following points without altering any configuration:
1. **Device History & Inventory**: Query DHCP lease tables, ARP tables, and historical device lists.
2. **ISP Remote Management (TR-069 / CWMP)**: Check if connection/WAN profiles contain `TR069`, `CWMP`, `ACS`, or active remote support tunnels managed by the ISP.
3. **Firmware & Update Visibility**: Check running firmware version, build date, and whether automatic/user updates are disabled by the ISP.
4. **DNS Configuration & Leaks**: Check upstream DNS servers assigned via DHCP/WAN. Run `scripts/dns-check.sh` to determine which provider answers queries.
5. **Logs & Telemetry**: Inspect system logs for connection timestamps, login events, and outbound vendor/telemetry reporting.

### Step 4: Summary Report
Format the findings into three clean, actionable sections:
1. **What your router knows**: Count of remembered devices, connected device details, logs retained.
2. **What your provider can see & reach**: TR-069 status, DNS query exposure, remote access channels.
3. **How to fix it**: Step-by-step guidance on changing default admin passwords, enabling Encrypted DNS (DoH/DoT), enabling Private MAC addresses, appending `_nomap` to Wi-Fi SSID, and rotating Wi-Fi passwords.

---

## Workflow 2: Fix Slow Wi-Fi

Triggered by queries like:
- *"My Wi-Fi is slow, fix it"*
- *"Why is my internet laggy?"*
- *"Optimize my router channel"*

### Step 1: Diagnostics
1. Check signal strength (RSSI), current band (2.4 GHz vs 5 GHz / 6 GHz), and channel width.
2. Scan neighboring Wi-Fi networks to identify co-channel and adjacent-channel interference.
3. Inspect active client count and bandwidth usage to locate high-traffic background devices.
4. Check router CPU/memory load and WAN port link negotiation speed (e.g. 100 Mbps vs 1000 Mbps).

### Step 2: Identification & Proposed Fixes
Identify the specific bottleneck:
- Congested 2.4 GHz channel (propose switching to 5 GHz or changing channel to 1, 6, or 11).
- Suboptimal channel width (e.g. 20 MHz vs 40/80 MHz).
- Co-channel interference from nearby access points.
- ISP/WAN negotiation or DNS resolution latency.

### Step 3: Authorization & Controlled Execution
1. Present the diagnosis and the exact proposed setting modification to the user.
2. **Wait for explicit user confirmation** before issuing any change.
3. Apply the authorized setting via the router's local API.
4. Re-verify connectivity and latency after application.
