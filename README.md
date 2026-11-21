<div align="center">

# Reverse Engineering Wi-Fi Router

### Comprehensive Framework for Reverse Engineering Wi-Fi Router Firmware, Admin APIs, TR-069 Telemetry, and Wireless Security Architecture

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Platform: Claude Code](https://img.shields.io/badge/Platform-Claude%20Code-5A32A3.svg?style=flat-square)](SKILL.md)
[![Scope: Local Subnet Only](https://img.shields.io/badge/Scope-Local%20Subnet%20Only-2ea44f.svg?style=flat-square)](#security-and-zero-leakage-architecture)
[![Interface: CLI and Prompts](https://img.shields.io/badge/Interface-CLI%20%26%20Prompts-informational.svg?style=flat-square)](#deployment-and-usage-protocols)
[![Topic: Router Reverse Engineering](https://img.shields.io/badge/Topic-Reverse%20Engineering%20Wi--Fi%20Router-orange.svg?style=flat-square)](https://github.com/smartworldarafath/Reverse-Engineer-WiFi-Router)

<p align="center">
  A disciplined open-source security engineering framework and autonomous agent skill dedicated to reverse engineering Wi-Fi router systems, discovering undocumented administrative endpoints, auditing carrier TR-069 ACS telemetry channels, and eliminating wireless performance bottlenecks strictly within local operational boundaries.
</p>

</div>

---

## Executive Summary

**Reverse Engineering Wi-Fi Router** (`Reverse-Engineer-WiFi-Router`) is an authoritative technical specification, Claude Code agent skill, and defensive security toolkit. It is engineered for security researchers, network engineers, and system administrators seeking to reverse engineer Wi-Fi router hardware, firmware architectures, and internal communication protocols without damaging equipment or violating operational boundaries.

Consumer Customer Premises Equipment (CPE) -- including Wi-Fi routers, broadband gateways, and optical network terminals (ONTs) -- forms the crucial defensive perimeter between private local area networks (LANs) and public wide area networks (WANs). However, most consumer gateways operate proprietary, closed-source firmware containing undocumented administrative endpoints, persistent ISP monitoring daemons, unencrypted DNS forwarders, and persistent client logging.

This project provides a reproducible, step-by-step methodology for reverse engineering Wi-Fi router interfaces, mapping internal JSON-RPC and CGI APIs, inspecting carrier-level CWMP (TR-069/TR-369) management channels, and hardening wireless infrastructure.

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Why Reverse Engineering Wi-Fi Router Gateways Matters](#why-reverse-engineering-wi-fi-router-gateways-matters)
- [Threat Model and Attack Surface Analysis](#threat-model-and-attack-surface-analysis)
  - [1. Carrier Remote Management Channels (TR-069 / CWMP)](#1-carrier-remote-management-channels-tr-069--cwmp)
  - [2. Unencrypted DNS Query Interception](#2-unencrypted-dns-query-interception)
  - [3. Geolocation Triangulation via BSSID Harvesting](#3-geolocation-triangulation-via-bssid-harvesting)
  - [4. UPnP Dynamic Port Mapping and IGD Traversal](#4-upnp-dynamic-port-mapping-and-igd-traversal)
- [Step-by-Step Wi-Fi Router Reverse Engineering Methodology](#step-by-step-wi-fi-router-reverse-engineering-methodology)
  - [Phase 1: Hardware Identification and SoC Profiling](#phase-1-hardware-identification-and-soc-profiling)
  - [Phase 2: Gateway Discovery and Subnet Enumeration](#phase-2-gateway-discovery-and-subnet-enumeration)
  - [Phase 3: Administrative Web Surface Reverse Engineering](#phase-3-administrative-web-surface-reverse-engineering)
  - [Phase 4: Undocumented API Endpoint Mapping](#phase-4-undocumented-api-endpoint-mapping)
- [Operational Workflows](#operational-workflows)
  - [Workflow 1: Read-Only Privacy and Telemetry Audit](#workflow-1-read-only-privacy-and-telemetry-audit)
  - [Workflow 2: Wireless Performance Optimization](#workflow-2-wireless-performance-optimization)
- [Security and Zero-Leakage Architecture](#security-and-zero-leakage-architecture)
  - [Local Keyring Integration](#local-keyring-integration)
  - [Real-Time Stream Masking](#real-time-stream-masking)
- [Empirical Case Study: Consumer Gateway Telemetry Audit](#empirical-case-study-consumer-gateway-telemetry-audit)
- [Deployment and Usage Protocols](#deployment-and-usage-protocols)
  - [Claude Code Agent Skill Installation](#claude-code-agent-skill-installation)
  - [Standalone Technical Prompts](#standalone-technical-prompts)
- [Diagnostic Utilities Reference](#diagnostic-utilities-reference)
  - [DNS Resolution Verifier: scripts/dns-check.sh](#dns-resolution-verifier-scriptsdns-checksh)
  - [PII and Secret Sanitizer: scripts/mask.py](#pii-and-secret-sanitizer-scriptsmaskpy)
- [CPE Hardening and Remediation Protocol](#cpe-hardening-and-remediation-protocol)
- [Academic Research and Formal References](#academic-research-and-formal-references)
- [Supported Hardware and Firmware Ecosystems](#supported-hardware-and-firmware-ecosystems)
- [Technical Frequently Asked Questions](#technical-frequently-asked-questions)
- [Contribution Standards](#contribution-standards)
- [License and Legal Disclaimer](#license-and-legal-disclaimer)

---

## Why Reverse Engineering Wi-Fi Router Gateways Matters

Modern broadband gateways are embedded computers running variants of Linux (OpenWrt, BusyBox, LuCI, eCos, or proprietary vendor kernels). Despite their critical role in household and corporate security, they suffer from fundamental transparency issues:

1. **Undocumented Administrative APIs:** Web interfaces communicate with underlying daemons through undocumented HTTP POST endpoints, JSON-RPC endpoints, or legacy CGI routines. Reverse engineering Wi-Fi router web interfaces exposes these endpoints for automation and auditing.
2. **Hidden ISP Telemetry Daemons:** Internet service providers routinely configure Auto-Configuration Server (ACS) daemons using the TR-069 / TR-369 protocol. These daemons maintain persistent connections to upstream ISP infrastructure, allowing remote configuration changes, telemetry extraction, and firmware updates without user knowledge.
3. **Pervasive DNS Tracking:** Most routers forward all local domain lookups in cleartext to ISP DNS servers, exposing every browsing session to passive eavesdropping.
4. **Persistent Client Association History:** Many consumer routers record device MAC addresses, device hostnames, and connection timestamps permanently in local flash memory or volatile RAM tables.

---

## Threat Model and Attack Surface Analysis

When conducting Wi-Fi router reverse engineering, the gateway architecture is evaluated across four core attack vectors:

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
|  | Embedded Services:                                              |  |
|  | - Web Console (lighttpd, uHTTPd, mini_httpd, Boa, nginx)       |  |
|  | - Remote Agent (cwmp, tr069client, acs_client, tr181)           |  |
|  | - Port Mapping (miniupnpd, IGD daemon)                          |  |
|  | - Resolver Proxy (dnsmasq, unbound, system resolver)           |  |
|  | - Telemetry Storage (ARP cache, DHCP lease table, syslog)       |  |
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

### 1. Carrier Remote Management Channels (TR-069 / CWMP)
Carrier broadband gateways implement the TR-069 (CWMP) protocol over SOAP/XML. An active `TR069_INTERNET` WAN profile or ACS client allows external servers to query internal routing tables, retrieve connected client lists, and modify router settings. Reverse engineering the router's configuration tables reveals the ACS server URL, inform intervals, and credential states.

### 2. Unencrypted DNS Query Interception
By default, consumer gateways deploy `dnsmasq` or embedded resolver forwarders that route queries to upstream telecom resolvers in cleartext. Without DNS-over-HTTPS (DoH) or DNS-over-TLS (DoT), all domain lookups are visible to intermediate network entities.

### 3. Geolocation Triangulation via BSSID Harvesting
Wireless Access Points periodically broadcast 802.11 beacon frames containing their Basic Service Set Identifier (BSSID). Commercial positioning databases (Apple, Google, Skyhook) index BSSIDs alongside physical GPS coordinates gathered from mobile devices. Appending `_nomap` to the SSID prevents insertion into these registries.

### 4. UPnP Dynamic Port Mapping and IGD Traversal
Active Universal Plug and Play (UPnP) IGD daemons permit unauthenticated devices on the local subnet to open inbound public WAN ports, bypassing firewall protections without administrative confirmation.

---

## Step-by-Step Wi-Fi Router Reverse Engineering Methodology

The framework utilizes a systematic, non-invasive methodology for reverse engineering Wi-Fi router devices:

### Phase 1: Hardware Identification and SoC Profiling
1. Examine external chassis design, antenna configuration, and port layout (with serial/credential stickers occluded).
2. Cross-reference FCC ID records and hardware revision indicators to determine the internal System-on-Chip (SoC) family:
   - Broadcom (BCM series)
   - MediaTek / Ralink (MT76xx series)
   - Qualcomm Atheros (QCA series)
   - Realtek (RTL series)
3. Identify the base firmware family (OpenWrt derivative, Asuswrt, embedded proprietary RTOS).

### Phase 2: Gateway Discovery and Subnet Enumeration
Identify the primary gateway interface on the active operating system:
- **macOS:** `route -n get default`
- **Linux:** `ip route show default`
- **Windows:** `Get-NetRoute -DestinationPrefix '0.0.0.0/0'` or `ipconfig`

### Phase 3: Administrative Web Surface Reverse Engineering
Inspect the HTTP/HTTPS management server listening on the gateway IP:
- Analyze server response headers (`Server: mini_httpd`, `Server: uHTTPd`, `Server: lighttpd`).
- Inspect the DOM tree and client-side JavaScript source of the login portal.
- Deconstruct client-side authentication mechanisms (MD5 challenge-response, SHA-256 PBKDF2 iterations, AES token wrappers).

### Phase 4: Undocumented API Endpoint Mapping
Identify hidden management endpoints:
- Dynamic CGI dispatchers (`/cgi-bin/luci`, `/apply.cgi`, `/router_status.cgi`).
- Asynchronous JSON-RPC channels (`/ubus`, `/api/v1/status`).
- Dynamic script parameter reflection (`/asp/status.asp`, `/data/wan_info.json`).

The agent logs verified endpoints in a structured local mapping table for subsequent read-only auditing or performance optimization.

---

## Operational Workflows

### Workflow 1: Read-Only Privacy and Telemetry Audit

This workflow conducts an exhaustive inspection of router privacy parameters without modifying system state:

```
+-----------------------------------------------------------------------+
|           Phase 1: Gateway and Authentication Handshake               |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|               Phase 2: Core Data Collection Matrix                    |
|  - Active & Historical DHCP/ARP Tables (MAC, IP, Hostname, Leases)    |
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
|  - Local Interface Verification (scripts/mask.py)                     |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|           Phase 4: Synthesis and Hardening Report Formulation         |
+-----------------------------------------------------------------------+
```

The output report delivers three actionable sections:
1. **Internal Data Retention:** Device logs, stored hardware addresses, and connection history.
2. **External Telemetry Exposure:** TR-069 management links, DNS leakage, and carrier control surfaces.
3. **Remediation Plan:** Vendor-neutral hardening instructions for closing identified exposures.

---

### Workflow 2: Wireless Performance Optimization

When experiencing latency spikes, packet loss, or throughput degradation, the optimization workflow diagnoses and refines wireless settings under strict user authorization:

1. **Environmental Assessment:**
   - Evaluates Received Signal Strength Indicator (RSSI) and Signal-to-Noise Ratio (SNR).
   - Scans 2.4 GHz, 5 GHz, and 6 GHz spectrums to detect co-channel and adjacent-channel interference.
   - Evaluates band steering policies and 802.11k/v/r fast-roaming support.
2. **Channel and Bandwidth Tuning:**
   - Evaluates channel widths (20 MHz, 40 MHz, 80 MHz, 160 MHz) against environmental noise floors.
   - Audits Ethernet PHY negotiation speeds (100 Mbps vs 1 Gbps vs 2.5 Gbps) to detect duplex mismatches.
3. **Controlled Modification Protocol:**
   - Creates a snapshot of current router settings before changes.
   - Displays proposed modifications (`old_value -> new_value`).
   - Requires explicit human approval (`yes`) prior to transmitting write requests.
   - Executes automated post-change connectivity checks with immediate rollback capability.

---

## Security and Zero-Leakage Architecture

To ensure sensitive network credentials and telemetry data are never exposed, this framework strictly follows local zero-leakage security protocols:

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

### Local Keyring Integration
Administrative credentials are never pasted into chat contexts. Instead, credentials reside in host OS secure keyrings:
- **macOS:** `security add-generic-password -s "wifi-router-admin" -a "admin" -w "<password>"`
- **Windows:** `cmdkey /generic:wifi-router-admin /user:admin /pass:"<password>"`
- **Linux:** `secret-tool store --label="wifi-router-admin" service wifi-router-admin username admin`

Local scripts read credentials dynamically via standard input pipes at runtime.

### Real-Time Stream Masking
All diagnostic streams pass through `scripts/mask.py` prior to display. The sanitization engine applies regex transformations to neutralize sensitive identifiers:

| Identifier Type | Raw Input Example | Sanitized Output |
| :--- | :--- | :--- |
| **Public IPv4 Address** | `203.0.113.45` | `203.0.x.x` |
| **Global IPv6 Address** | `2001:db8:85a3::8a2e:370:7334` | `xxxx:xxxx::xxxx` |
| **Device MAC Address** | `b4:5d:50:8f:92:1a` | `b4:5d:50:**:**:**` |
| **Hardware Serial Number** | `SN: 210235A1BC29381` | `SN: ****` |
| **Wireless SSID (XML/JSON)** | `<ssid>HomeNetwork_5G</ssid>` | `<ssid>****</ssid>` |
| **Host Workstation Name** | `DESKTOP-8K7J49Q` | `DESKTOP-****` |

---

## Empirical Case Study: Consumer Gateway Telemetry Audit

The following table summarizes empirical parameters captured during a privacy audit of a tier-1 ISP fiber optical network terminal (ZTE / Huawei hybrid gateway platform):

| Inspection Vector | Observed Gateway State | Privacy and Security Implication |
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

### Claude Code Agent Skill Installation

Install the repository as a global skill:

```bash
git clone https://github.com/smartworldarafath/Reverse-Engineer-WiFi-Router.git ~/.claude/skills/reverse-engineer-wifi-router
```

Connect your computer to the target Wi-Fi network, launch your AI agent, provide an image of the router chassis (covering serial stickers), and execute:

```text
what does my router know about me?
```

or

```text
my Wi-Fi is slow, fix it
```

### Standalone Technical Prompts

If executing without local agent skill loaders, run the standalone prompts directly:
- **Privacy Audit:** [`prompts/privacy-check.md`](prompts/privacy-check.md)
- **Performance Optimization:** [`prompts/fix-slow-wifi.md`](prompts/fix-slow-wifi.md)

---

## Diagnostic Utilities Reference

### DNS Resolution Verifier: `scripts/dns-check.sh`

`dns-check.sh` interrogates authoritative Akamai verification resolvers to identify the upstream resolver handling workstation requests:

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

`mask.py` is an automated stream sanitizer designed to neutralize PII, MAC addresses, public IP addresses, and session credentials before logs are rendered in terminal windows:

```bash
# Pipe any standard diagnostic command output
ipconfig /all | python3 scripts/mask.py

# Pipe router JSON API status responses
curl -s http://192.168.1.1/api/status | python3 scripts/mask.py
```

---

## CPE Hardening and Remediation Protocol

Follow this structured remediation workflow to harden consumer router hardware:

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

1. **Encrypted DNS Configuration:** Deploy DNS-over-HTTPS (DoH) across endpoints (Android Private DNS, Windows 11 Encrypted DNS, iOS configuration profiles, Chrome/Firefox Secure DNS).
2. **MAC Address Randomization:** Enable private MAC addressing on client operating systems to prevent permanent client tracking.
3. **Geolocation Database Opt-Out (`_nomap`):** Append `_nomap` to all operational SSIDs to prevent Wi-Fi Positioning Systems from indexing your access point BSSID.
4. **Channel and Band Isolation:** Restrict 2.4 GHz channels strictly to non-overlapping channels **1, 6, or 11** at **20 MHz** width. Migrate high-bandwidth devices to **5 GHz** or **6 GHz** at 80 MHz channel widths.

---

## Academic Research and Formal References

This framework draws upon peer-reviewed cybersecurity literature:

1. **Carrier-Scale TR-069 Deployment Vulnerabilities:**  
   *Hils, M., & Böhme, R. (2020).* "Watching the Weak Link into Your Home: A Systematic Large-Scale Study of the TR-069 Ecosystem." *Applied Cryptography and Network Security (ACNS 2020)*. Lecture Notes in Computer Science, vol 12146. Springer, Cham.  
   Preprint: [arXiv:2001.02564](https://arxiv.org/abs/2001.02564).  
   *Analyzed approximately 1 billion broadband endpoints operating active TR-069 CPE management agents vulnerable to misconfiguration and unauthorized configuration extraction.*

2. **Global Wireless Surveillance via BSSID Positioning:**  
   *Rye, E. C., & Levin, D. (2024).* "Surveilling the Masses with Wi-Fi-Based Positioning Systems." *Proceedings of the ACM on Measurement and Analysis of Computing Systems (SIGMETRICS 2024)*.  
   Preprint: [arXiv:2405.14975](https://arxiv.org/abs/2405.14975).  
   *Demonstrated that Wi-Fi Positioning Systems (WPS) permit third parties to track device mobility, household coordinates, and perimeter hardware across billions of consumer BSSIDs.*

---

## Supported Hardware and Firmware Ecosystems

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

#### Q1: Does Reverse Engineering Wi-Fi Router modify flash memory or NVRAM?
No. The framework operates exclusively at the application and management layers of the router's existing administration console. It does not overwrite bootloaders, write to flash partitions, or install custom kernel packages.

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

## License and Legal Disclaimer

### License
This project is licensed under the terms of the **[MIT License](LICENSE)**.

### Legal Disclaimer
This software is provided for defensive security evaluation, privacy auditing, and network optimization purposes strictly on hardware owned by the operator or on networks where explicit operational authorization has been granted. Inspecting, auditing, or modifying network infrastructure without administrative rights is strictly prohibited. The maintainers assume no liability for misuse or operational interruption resulting from the use of this toolkit.
