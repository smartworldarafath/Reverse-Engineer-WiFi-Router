<div align="center">

# Reverse-Engineer Wi-Fi Router

### Autonomous Security Auditing, Local API Discovery, and Telemetry Analysis for Consumer Gateway Architecture

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Platform: Claude Code](https://img.shields.io/badge/Platform-Claude%20Code-5A32A3.svg?style=flat-square)](SKILL.md)
[![Scope: Local Subnet Only](https://img.shields.io/badge/Scope-Local%20Subnet%20Only-2ea44f.svg?style=flat-square)](#security-and-zero-leakage-architecture)
[![Interface: CLI and Prompts](https://img.shields.io/badge/Interface-CLI%20%26%20Prompts-informational.svg?style=flat-square)](#deployment-and-usage-protocols)

<p align="center">
  A disciplined security framework and agent skill for identifying Customer Premises Equipment (CPE) firmware interfaces, auditing hidden ISP telemetry channels, and diagnosing wireless bottlenecks strictly within local operational boundaries.
</p>

</div>

---

## Table of Contents

- [Abstract and System Overview](#abstract-and-system-overview)
- [Threat Model and Attack Surface Analysis](#threat-model-and-attack-surface-analysis)
- [Reverse-Engineering Methodology](#reverse-engineering-methodology)
- [Operational Workflows](#operational-workflows)
  - [Workflow 1: Read-Only Privacy and Telemetry Audit](#workflow-1-read-only-privacy-and-telemetry-audit)
  - [Workflow 2: Wireless Performance Optimization](#workflow-2-wireless-performance-optimization)
- [Security and Zero-Leakage Architecture](#security-and-zero-leakage-architecture)
- [Empirical Case Study: Consumer Gateway Telemetry](#empirical-case-study-consumer-gateway-telemetry)
- [Deployment and Usage Protocols](#deployment-and-usage-protocols)
  - [Agent Skill Installation](#agent-skill-installation)
  - [Standalone Prompt Execution](#standalone-prompt-execution)
- [Diagnostic Utilities Reference](#diagnostic-utilities-reference)
  - [DNS Resolution Verifier: scripts/dns-check.sh](#dns-resolution-verifier-scriptsdns-checksh)
  - [PII and Secret Sanitizer: scripts/mask.py](#pii-and-secret-sanitizer-scriptsmaskpy)
- [CPE Hardening and Remediation Protocol](#cpe-hardening-and-remediation-protocol)
- [Academic Research and Formal References](#academic-research-and-formal-references)
- [Supported Hardware and Firmware Ecosystems](#supported-hardware-and-firmware-ecosystems)
- [Technical Frequently Asked Questions](#technical-frequently-asked-questions)
- [Contribution Standards](#contribution-standards)
- [License and Disclaimer](#license-and-disclaimer)

---

## Abstract and System Overview

Consumer Customer Premises Equipment (CPE)—commonly marketed as Wi-Fi routers, broadband gateways, and optical network terminals (ONTs)—operates at the critical boundary between trusted private local area networks (LANs) and untrusted wide area networks (WANs). Despite occupying this privileged position, contemporary consumer routing hardware suffers from pervasive security and privacy deficiencies:

1. **Undocumented Administrative Interfaces:** Web management panels often utilize undocumented internal JSON-RPC endpoints, legacy CGI scripts, or hidden asynchronous endpoints designed without public API contracts.
2. **Persistent ISP Remote Management:** Millions of ISP-supplied gateways run pre-configured Auto-Configuration Server (ACS) daemons implementing the CPE WAN Management Protocol (TR-069 / TR-369 CWMP), allowing upstream network operators unfettered remote access, telemetry harvesting, and forced firmware pushes without subscriber notification.
3. **Pervasive Unencrypted Resolution:** Default gateway configurations consistently forward all LAN DNS queries in cleartext through regional telecom resolvers, exposing full host domain lookup patterns to intermediate wiretaps and passive ISP inspection.
4. **Permanent Hardware Logging:** Devices maintain persistent historical tables of physical MAC addresses, hostnames, and connection timestamps long after transient clients disconnect.

**Reverse-Engineer Wi-Fi Router** (`Reverse-Engineer-WiFi-Router`) is an open-source technical specification, Claude Code agent skill, and standalone prompt toolkit. It enables AI coding and security agents to visually inspect physical router chassis hardware, deduce administrative web endpoints, interact with internal APIs without credential exposure, audit active ISP telemetry channels, and optimize wireless configurations under strict user consent.

---

## Threat Model and Attack Surface Analysis

The operational model analyzes the local gateway across four primary threat vectors:

```
+-----------------------------------------------------------------------+
|                         Wide Area Network (WAN)                       |
|  +-----------------------------------------------------------------+  |
|  |   Upstream ISP / ACS Server (TR-069 / CWMP Remote Management)   |  |
|  +-----------------------------------------------------------------+  |
|                                   |                                   |
|                          WAN Port Interface                           |
+-----------------------------------|-----------------------------------+
                                    |
+-----------------------------------|-----------------------------------+
|               Customer Premises Equipment (CPE Gateway)               |
|                                   v                                   |
|  +-----------------------------------------------------------------+  |
|  | Gateway OS (Linux Kernel, BusyBox, LuCI, eCos, Proprietary RTOS)|  |
|  +-----------------------------------------------------------------+  |
|  | Services:                                                       |  |
|  | - Web Console (lighttpd, uHTTPd, mini_httpd, Boa)               |  |
|  | - Remote Agent (cwmp, tr069client, acs_client)                  |  |
|  | - Port Mapping (miniupnpd, IGD daemon)                          |  |
|  | - Resolver Proxy (dnsmasq, unbound, system resolver)           |  |
|  | - Telemetry Storage (ARP cache, DHCP lease table, system logs)  |  |
|  +-----------------------------------------------------------------+  |
|                                   |                                   |
+-----------------------------------|-----------------------------------+
                                    |
                     Local Area Network (LAN / WLAN)
                                    |
      +-----------------------------+-----------------------------+
      |                             |                             |
      v                             v                             v
+------------+               +------------+               +---------------+
| Workstation|               | Smartphone |               | Smart TV Box  |
| (Local AI) |               | (Random MAC|               | (Hidden Apps) |
+------------+               +------------+               +---------------+
```

### 1. Carrier Remote Access Vectors (TR-069 / CWMP)
Broadband carriers utilize TR-069 (CWMP) to administer subscriber endpoints over HTTP/SOAP. An active `TR069_INTERNET` WAN profile or listening ACS client exposes device parameters—including internal routing tables, associated client identifiers, and wireless configuration files—to upstream queries. If the carrier Auto-Configuration Server is compromised or operates with deprecated TLS configurations, the subscriber network perimeter is completely breached.

### 2. DNS Query Exposure and Cleartext Interception
Standard CPE gateways deploy local caching forwarders (`dnsmasq`) configured to upstream queries directly to ISP-assigned recursive resolvers. Without DNS-over-HTTPS (DoH) or DNS-over-TLS (DoT), every hostname resolution traversing the WAN interface is subject to passive eavesdropping, SNI correlation, and DNS poisoning.

### 3. Geolocation Triangulation via BSSID Harvesting
Wireless Access Points periodically transmit 802.11 beacon frames containing their Basic Service Set Identifier (BSSID). Commercial positioning systems (Apple Location Services, Google Location Services) correlate mapped BSSIDs with GPS coordinates gathered from passing mobile devices. Unless access point SSIDs incorporate the `_nomap` opt-out suffix, physical household coordinates remain cataloged in global databases.

### 4. UPnP / NAT-PMP IGD Traversal
Active Universal Plug and Play (UPnP) Internet Gateway Device (IGD) services allow unauthenticated endpoints on the local subnet to dynamically map public WAN ports to internal hosts, bypassing perimeter firewall policies without administrative intervention.

---

## Reverse-Engineering Methodology

The framework operates via a progressive discovery pipeline:

1. **Hardware Profiling from Physical Signatures:** The operator provides a photograph of the physical router chassis with all credential labels occluded. The model identifies:
   - Vendor, chassis architecture, and commercial model nomenclature.
   - FCC ID, hardware revision indicators, and industrial design cues.
   - Underlying System-on-Chip (SoC) family (Broadcom, MediaTek, Qualcomm Atheros, Realtek).
   - Expected firmware distribution (OpenWrt derivative, Asuswrt, vendor-modified embedded Linux).

2. **Gateway Discovery and Subnet Identification:** The agent interrogates local network subsystem interfaces to identify the primary default gateway:
   - macOS: `route -n get default`
   - Linux: `ip route show default`
   - Windows: `Get-NetRoute -DestinationPrefix '0.0.0.0/0'` or `ipconfig`

3. **Administrative Surface Enumeration:** Upon locating the gateway address (e.g., `192.168.1.1`), the agent probes the HTTP/HTTPS listeners:
   - Inspects response headers (`Server: mini_httpd`, `Server: uHTTPd`, `Server: lighttpd`).
   - Evaluates the DOM and client-side JavaScript source of the login interface.
   - Deconstructs client-side hashing algorithms (MD5 challenge-response, SHA-256 PBKDF2 iterations, AES encryption wrappers) utilized during authentication.

4. **API Endpoint Mapping:** Home router management consoles rarely expose structured REST APIs with OpenAPI specifications. Instead, they operate through internal mechanisms:
   - Asynchronous form posts via hidden CGI scripts (`/cgi-bin/luci`, `/apply.cgi`, `/router_status.cgi`).
   - Internal JSON-RPC dispatchers (`/ubus`, `/api/v1/status`).
   - Dynamic script parameter reflection (`/asp/status.asp`, `/data/wan_info.json`).

The agent constructs an internal map of these endpoints, cataloging paths, request types, and token dependencies into a local configuration artifact.

---

## Operational Workflows

### Workflow 1: Read-Only Privacy and Telemetry Audit

This workflow extracts configuration and telemetry data without modifying device state:

```
+-----------------------------------------------------------------------+
|           Phase 1: Gateway and Authentication Handshake               |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|               Phase 2: Core Data Collection Matrix                    |
|  - Active/Historical DHCP & ARP Tables (MAC, IP, Hostname, Leases)    |
|  - WAN Profiles & Remote Management Channels (TR-069, CWMP, ACS)      |
|  - Firmware Release Timestamp, Kernel Version & Update Mechanisms     |
|  - Recursive DNS Forwarders, Dynamic Upstream Servers, Root Resolvers |
|  - UPnP Dynamic Port Forwarding Rules & Static NAT Mappings           |
|  - Event Audit Logs, Login Timestamps & External Syslog Forwarding    |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|           Phase 3: Workstation-Level Verification Checks             |
|  - Upstream Resolver Identity (scripts/dns-check.sh)                  |
|  - Route Path & Carrier-Grade NAT (CGNAT) Hop Discovery (traceroute)  |
|  - Optional: Android TV / ADB Netstats Inspection (If Authorized)     |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|           Phase 4: Synthesis and Hardening Report Formulation         |
+-----------------------------------------------------------------------+
```

The output report delivers three explicit deliverables:
1. **What your router knows:** Full accounting of persistent device logs, hardware addresses, and connection records.
2. **What your provider can see:** Complete status of TR-069 management links, DNS exposure, and carrier control surfaces.
3. **How to fix it:** Concrete, vendor-neutral remediation steps targeting each identified gap.

---

### Workflow 2: Wireless Performance Optimization

When performance degradation or high latency occurs, the agent executes diagnostic and tuning routines under explicit user supervision:

1. **Environmental Assessment:**
   - Evaluates signal-to-noise ratio (SNR) and Received Signal Strength Indicator (RSSI).
   - Detects channel utilization and co-channel interference from adjacent access points across 2.4 GHz, 5 GHz, and 6 GHz spectrums.
   - Evaluates client band steering policies and 802.11k/v/r roaming capabilities.
2. **Configuration Comparison:**
   - Compares active channel widths (20 MHz, 40 MHz, 80 MHz, 160 MHz) against physical interference limits.
   - Audits physical layer (PHY) negotiation speeds and duplex modes across WAN/LAN Ethernet ports.
3. **Change Control Protocol:**
   - Backs up current device configuration state prior to any modification.
   - Displays exact proposed parameter changes (`old_value -> new_value`).
   - Requires explicit operator authorization (`yes`) before sending write requests to the API.
   - Performs automated post-change validation and provides immediate rollback routines.

---

## Security and Zero-Leakage Architecture

To protect home network credentials and sensitive infrastructure data, this framework enforces strict technical controls:

```
[ Local User Terminal ] 
       |
       | 1. Generate Keystore Command (System-Level)
       v
+------------------------------------------------------------------+
| Operating System Secure Storage (Keychain / CredMgr / SecretTool)|
+------------------------------------------------------------------+
       |
       | 2. Retrieve Secret In Local Shell Script (Never in Chat)
       v
[ Router Administrative Interface ]
       |
       | 3. Raw Diagnostic Stream
       v
+------------------------------------------------------------------+
| Sanitization Engine (scripts/mask.py)                            |
| - Redacts Public IPv4 & IPv6 Addresses                           |
| - Masks Device-Specific MAC Octets (XX:XX:XX:__:__:__)           |
| - Strips Serial Numbers, Passphrases, and BSSIDs                 |
| - Masks Host PC Names (DESKTOP-*, LAPTOP-*)                      |
+------------------------------------------------------------------+
       |
       | 4. Sanitized Diagnostic Output
       v
[ AI Context / User Display ]
```

### Credential Protection Guarantee
- Router administrative passwords must never be input into the chat interface.
- The framework generates native system commands to store the password in the host OS credential manager:
  - **macOS:** `security add-generic-password -s "wifi-router-admin" -a "admin" -w "<password>"`
  - **Windows:** `cmdkey /generic:wifi-router-admin /user:admin /pass:"<password>"`
  - **Linux:** `secret-tool store --label="wifi-router-admin" service wifi-router-admin username admin`
- Authentication scripts read credentials directly from system keychains at runtime via local subprocess pipes.

### Data Sanitization Protocol
Diagnostic output streams must be piped through `scripts/mask.py` prior to display. The sanitization engine applies regex transformations to neutralize private data:

| Sensitive Identifier | Raw Format Pattern | Masked Output Representation |
| :--- | :--- | :--- |
| **Public IPv4 Address** | `203.0.113.45` | `203.0.x.x` |
| **Global IPv6 Address** | `2001:db8:85a3::8a2e:370:7334` | `xxxx:xxxx::xxxx` |
| **Device MAC Address** | `b4:5d:50:8f:92:1a` | `b4:5d:50:**:**:**` |
| **Hardware Serial Number** | `SN: 210235A1BC29381` | `SN: ****` |
| **Wireless SSID (XML/JSON)** | `<ssid>HomeNetwork_5G</ssid>` | `<ssid>****</ssid>` |
| **Host Workstation Identifier**| `DESKTOP-8K7J49Q` | `DESKTOP-****` |

---

## Empirical Case Study: Consumer Gateway Telemetry

The following data table illustrates verified telemetry parameters captured from a standard tier-1 ISP fiber optical network gateway (ZTE / Huawei hybrid platform) during an audit:

| Inspection Vector | Factory / Observed State | Security and Privacy Implication |
| :--- | :--- | :--- |
| **Primary WAN Interface** | `1_TR069_INTERNET_R_VID_10` | The primary data route is permanently multiplexed with an ACS management tunnel. |
| **ACS Connection Status** | `PeriodicInform: Enabled (Interval: 86400s)` | The router transmits device parameters and network states to carrier servers daily. |
| **Client Association History**| `29 Records (11 Active, 18 Disconnected)` | Complete client inventory persists indefinitely across soft reboots. |
| **MAC Address Randomization** | `3 of 29 clients using Locally Administered bit` | 89.6% of connected endpoints expose their globally unique hardware addresses. |
| **Recursive DNS Upstream** | `103.x.x.1, 103.x.x.2 (ISP Autonomous System)` | 100% of internal DNS resolutions transit unencrypted across the carrier network. |
| **Firmware Maintenance** | `AutoUpdate: Enabled (User Manual Upload: Disabled)` | Device operator cannot audit, schedule, or restrict binary firmware updates. |
| **UPnP Port Assignments** | `Teredo (UDP 54223), BitTorrent (TCP 6881)` | Internal services exposed external listening ports without manual administrative approval. |

---

## Deployment and Usage Protocols

### Agent Skill Installation

To install as an active Claude Code skill:

```bash
git clone https://github.com/smartworldarafath/Reverse-Engineer-WiFi-Router.git ~/.claude/skills/reverse-engineer-wifi-router
```

Once installed, ensure your workstation is connected to the target home Wi-Fi network. Launch Claude Code, provide an image of the physical router chassis (with sensitive stickers covered), and submit standard command prompts:

```text
what does my router know about me?
```

or

```text
my Wi-Fi is slow, fix it
```

### Standalone Prompt Execution

If operating without local agent skill extensions, the workflow can be executed directly by pasting the prepared technical prompts into an active session:

- **Privacy Audit Prompt:** Copy the raw contents of [`prompts/privacy-check.md`](prompts/privacy-check.md) into the prompt context along with the router chassis photograph.
- **Performance Diagnostic Prompt:** Copy the raw contents of [`prompts/fix-slow-wifi.md`](prompts/fix-slow-wifi.md) into the prompt context to initiate channel and bandwidth diagnosis.

---

## Diagnostic Utilities Reference

### DNS Resolution Verifier: `scripts/dns-check.sh`

`dns-check.sh` queries authoritative Akamai verification endpoints to determine the outward-facing public resolver handling host queries:

```bash
#!/usr/bin/env bash
set -u

ip=""
if command -v dig >/dev/null 2>&1; then
  ip=$(dig +short whoami.akamai.net 2>/dev/null | grep -E '^[0-9.]+$' | tail -1)
fi
if [ -z "$ip" ] && command -v nslookup >/dev/null 2>&1; then
  ip=$(nslookup whoami.akamai.net 2>/dev/null | awk '/^Name:/ {found=1} found && /^Address/ {print $2}' | tail -1)
fi
if [ -z "$ip" ]; then
  echo "Could not resolve whoami.akamai.net"
  exit 1
fi

echo "Your DNS lookups are answered by: $(echo "$ip" | awk -F. '{print $1"."$2".x.x"}')"
if command -v whois >/dev/null 2>&1; then
  whois "$ip" 2>/dev/null | grep -iE '^(orgname|org-name|organization|descr|netname|owner):' | head -3
else
  echo "(install whois to see which company owns it)"
fi
```

### PII and Secret Sanitizer: `scripts/mask.py`

`mask.py` is a streaming filter designed to redact PII, hardware identifiers, and session tokens from diagnostic logs prior to terminal display:

```bash
# Pipe any command output through the sanitizer
ipconfig /all | python3 scripts/mask.py

# Pipe router JSON status responses
curl -s http://192.168.1.1/api/status | python3 scripts/mask.py
```

The script protects private subnets while retaining operational context:
- Retains local loopback (`127.0.0.1`), RFC 1918 private subnets (`192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`), and well-known public DNS resolvers (`1.1.1.1`, `8.8.8.8`, `9.9.9.9`).
- Replaces carrier-grade NAT (`100.64.0.0/10`) and public routable IPv4 blocks with partial masks (`203.0.x.x`).
- Redacts XML tags, quoted JSON parameters, and plain key-value assignments containing keys: `serial`, `ssid`, `bssid`, `passphrase`, `password`, `passwd`, `psk`, `wpa_key`.
- Normalizes and sanitizes hardware MAC addresses and Windows workstation hostnames (`DESKTOP-*`, `LAPTOP-*`).

---

## CPE Hardening and Remediation Protocol

Once the diagnostic baseline is established, apply the following systematic remediation steps:

```
[ Step 1: Credential Rotation ]
Rotate factory admin credentials from default values to high-entropy passphrases.
                 |
                 v
[ Step 2: Encrypted DNS (DoH/DoT) Activation ]
Route host lookups through authenticated, encrypted resolvers (Cloudflare, Quad9).
                 |
                 v
[ Step 3: Hardware Privacy Enforcement ]
Activate MAC randomization on all mobile endpoints; isolate IoT appliances.
                 |
                 v
[ Step 4: Geolocation Database Opt-Out ]
Append '_nomap' to all operational 2.4 GHz, 5 GHz, and 6 GHz SSIDs.
                 |
                 v
[ Step 5: Wireless Environment Optimization ]
Migrate clients to 5 GHz; restrict 2.4 GHz to clean non-overlapping channels (1, 6, 11).
```

### 1. Cryptographic DNS Hardening (DoH / DoT)
Eliminate plaintext carrier DNS snooping by deploying DNS-over-HTTPS across all active endpoints:
- **Android:** Navigate to `Settings > Network & internet > Private DNS` and configure a TLS endpoint (e.g., `one.one.one.one` or `dns.quad9.net`).
- **Microsoft Windows 11:** Navigate to `Network & internet > Wi-Fi > Hardware properties`, select `Edit DNS`, set to manual IPv4/IPv6, and select `Encrypted only (DNS over HTTPS)`.
- **Apple iOS / macOS:** Install an encrypted DNS configuration profile or utilize Cloudflare's verified 1.1.1.1 utility in DNS-only operational mode.
- **Web Browsers (Chrome / Firefox):** Enable `Use secure DNS` / `DNS over HTTPS` in advanced security preferences.

### 2. MAC Address Randomization
Enforce private hardware addresses on mobile client operating systems (iOS `Private Wi-Fi Address`, Android `Use randomized MAC`) to prevent router-side client tracking across network re-associations.

### 3. Geolocation Registry Opt-Out (`_nomap`)
Append the suffix `_nomap` to your wireless Network Name / SSID (e.g., `Enterprise_Gateway_nomap`). This signals to commercial geolocation mapping engines (Apple Location Services, Google Location Services) that the access point BSSID must not be indexed in global positioning registries.

### 4. Spectrum and Channel Isolation
- Disable legacy 802.11b rates to eliminate transmission airtime waste.
- Fix 2.4 GHz band allocations strictly to non-overlapping channels **1, 6, or 11** at **20 MHz** channel width to minimize adjacent-channel bleed.
- Migrate high-throughput workstations, media devices, and mobile units to **5 GHz** or **6 GHz** bands operating at 80 MHz channel widths.

---

## Academic Research and Formal References

The analytical scope of this toolkit builds upon empirical findings documented in the following peer-reviewed cybersecurity literature:

1. **Carrier-Scale TR-069 Deployment Vulnerabilities:**  
   *Hils, M., & Böhme, R. (2020).* "Watching the Weak Link into Your Home: A Systematic Large-Scale Study of the TR-069 Ecosystem." *Applied Cryptography and Network Security (ACNS 2020)*. Lecture Notes in Computer Science, vol 12146. Springer, Cham.  
   Preprint: [arXiv:2001.02564](https://arxiv.org/abs/2001.02564).  
   *Documenting empirical inspection of approximately 1 billion broadband endpoints operating active TR-069 CPE management agents vulnerable to misconfiguration and unauthorized configuration extraction.*

2. **Global Wireless Surveillance via BSSID Positioning:**  
   *Rye, E. C., & Levin, D. (2024).* "Surveilling the Masses with Wi-Fi-Based Positioning Systems." *Proceedings of the ACM on Measurement and Analysis of Computing Systems (SIGMETRICS 2024)*.  
   Preprint: [arXiv:2405.14975](https://arxiv.org/abs/2405.14975).  
   *Demonstrating that uncurated Wi-Fi Positioning Systems (WPS) allow third parties to track device mobility, household locations, and perimeter hardware across billions of consumer BSSIDs.*

---

## Supported Hardware and Firmware Ecosystems

This framework is vendor-neutral and designed to evaluate routers running standard embedded administrative systems:

| Hardware Vendor / OS Family | Management Interface Type | Typical Gateway Endpoints | Audit Feasibility |
| :--- | :--- | :--- | :--- |
| **OpenWrt / LuCI** | REST, JSON-RPC via `ubus`, CGI | `/cgi-bin/luci`, `/ubus` | Complete access |
| **Asuswrt / Merlin** | JSON endpoints, Hook CGI | `/appGet.cgi`, `/apply.cgi` | Complete access |
| **TP-Link (Archer / Deco)** | JSON-RPC over HTTP, Web API | `/`, `/cgi-bin/luci`, App proxy | High |
| **Netgear (Nighthawk / Orbi)** | SOAP, XML CGI, Dynamic ASP | `/soap/server_sa/`, `/core.cgi` | High |
| **Huawei / Honor Gateways** | Asynchronous JSON, Token ASP | `/api/system/`, `/html/index.html`| High |
| **ZTE Home Gateways** | REST JSON, JavaScript RPC | `/api/`, `/getmacro.cgi` | High |
| **Technicolor / Sagemcom** | Embedded Web Form, Broadcom CGI | `/status.cgi`, `/login.lp` | Moderate |
| **App-Only Mesh (Google Nest / eero)**| Proprietary Cloud API / Bluetooth | None (Local Web Console Disabled)| Subnet audit only |

---

## Technical Frequently Asked Questions

#### Q1: Does Reverse-Engineer Wi-Fi Router perform firmware flashing or modify low-level NVRAM?
No. The tool operates exclusively at the application and management layers of the router's existing administration console. It does not overwrite bootloaders, write to flash memory partitions, or install custom kernel packages.

#### Q2: Can this framework compromise or brick my device?
No. The privacy audit workflow is strictly read-only. In the performance optimization workflow, only standard wireless settings exposed by the manufacturer's own web panel (such as channel assignment or channel width) are adjusted, and every transaction requires explicit operator approval before execution.

#### Q3: How does the AI reverse-engineer the API without vendor documentation?
The AI inspects the client-side JavaScript architecture loaded by the browser during an administration session. Embedded web consoles download client scripts (`main.js`, `common.js`, `status.js`) that define internal request paths, variable structures, and authentication tokens. The AI maps these internal endpoints directly from the code.

#### Q4: What occurs if my gateway requires SMS two-factor authentication or a carrier account?
If a carrier gateway enforces multi-factor authentication or delegates authentication to an external cloud portal, the framework directs the operator to complete the authentication step within a standard browser window. Once the session cookie or authorization token is established, local telemetry inspection continues.

#### Q5: Is this tool compatible with app-only mesh systems (e.g., eero, Google Nest)?
Mesh systems that disable local HTTP/HTTPS management interfaces cannot be inspected via web scraping. For these units, the framework performs external subnet analysis: evaluating local DNS resolution paths, inspecting traceroute hops, and cataloging broadcast/multicast traffic traversing the LAN.

---

## Contribution Standards

Contributions, verified endpoint mappings, and diagnostic improvements are welcome. Please adhere to the following engineering standards:

1. **Zero External Attack Vectors:** Contributions must not incorporate brute-force dictionaries, vulnerability exploitation scripts, or tools designed to probe hosts beyond the local subnet.
2. **Deterministic Sanitization:** Any script or workflow contributing to terminal output must comply with `scripts/mask.py` sanitization standards.
3. **Verified Model Testing:** Pull requests documenting new router API models should specify vendor, firmware version, and verified endpoint paths.

```bash
git checkout -b feature/router-model-mapping
git commit -m "feat(api): add endpoint mapping for Huawei HG8145V5"
git push origin feature/router-model-mapping
```

---

## License and Disclaimer

### License
This project is licensed under the terms of the **[MIT License](LICENSE)**.

### Disclaimer
This software is provided for defensive security evaluation, privacy auditing, and network optimization purposes strictly on hardware owned by the operator or on networks where explicit operational authorization has been granted. Inspecting, auditing, or modifying network infrastructure without administrative rights is strictly prohibited. The maintainers assume no liability for misuse or operational interruption resulting from the use of this toolkit.
