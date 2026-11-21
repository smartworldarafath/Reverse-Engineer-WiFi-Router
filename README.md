<div align="center">

# Reverse Engineering Wi-Fi Router

### The Definitive Technical Framework for Reverse Engineering Wi-Fi Router Hardware, Firmware, Administrative APIs, TR-069 ACS Telemetry, and Embedded MIPS/ARM Daemons

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Platform: Claude Code](https://img.shields.io/badge/Platform-Claude%20Code-5A32A3.svg?style=flat-square)](SKILL.md)
[![Scope: Local Subnet Only](https://img.shields.io/badge/Scope-Local%20Subnet%20Only-2ea44f.svg?style=flat-square)](#security-and-zero-leakage-architecture)
[![Interface: CLI and Prompts](https://img.shields.io/badge/Interface-CLI%20%26%20Prompts-informational.svg?style=flat-square)](#deployment-and-usage-protocols)
[![Category: Reverse Engineering Wi-Fi Router](https://img.shields.io/badge/Category-Reverse%20Engineering%20Wi--Fi%20Router-orange.svg?style=flat-square)](https://github.com/smartworldarafath/Reverse-Engineer-WiFi-Router)

<p align="center">
  An authoritative, open-source security engineering framework and autonomous agent skill dedicated to reverse engineering Wi-Fi router systems. Covers physical UART/JTAG pinout discovery, SPI flash extraction, firmware file system carving (Binwalk), static binary decompilation (Ghidra/IDA), dynamic QEMU emulation, administrative web API reverse engineering, and carrier TR-069 ACS telemetry audits.
</p>

</div>

---

## Executive Summary

**Reverse Engineering Wi-Fi Router** (`Reverse-Engineer-WiFi-Router`) is an open-source technical specification, security audit framework, and autonomous agent skill. Designed for security researchers, embedded engineers, and penetration testers, this repository consolidates the entire lifecycle of reverse engineering Wi-Fi router devices:

1. **Hardware-Level Analysis:** Interrogating printed circuit boards (PCBs), identifying System-on-Chip (SoC) architectures, locating UART serial debug headers, and dumping non-volatile SPI NOR/NAND flash memory chips using hardware programmers.
2. **Firmware Extraction and Unpacking:** Carving root file systems (SquashFS, JFFS2, CramFS, UBIFS) from vendor binary images using Binwalk, unsquashfs, and custom extraction scripts.
3. **Embedded Binary Decompilation:** Disassembling MIPS32 and ARM embedded network binaries (`httpd`, `uHTTPd`, `boa`, `dnsmasq`, `hostapd`, `cwmp`) in Ghidra, IDA Pro, and Rizin to discover hardcoded credentials, buffer overflow conditions, and hidden command-injection parameters.
4. **Dynamic Emulation and Runtime Debugging:** Emulating router services across architectures using QEMU user-mode (`qemu-mips-static`, `qemu-arm-static`) and full-system emulators (Firmadyne, EMBA).
5. **Administrative Web API Reverse Engineering:** Reconstructing client-side hashing routines (MD5 challenge-response, PBKDF2, AES tokens) and mapping undocumented REST, JSON-RPC (`/ubus`), and CGI endpoints without public documentation.
6. **Carrier Telemetry and TR-069 Auditing:** Uncovering hidden Auto-Configuration Server (ACS) tunnels implementing the CPE WAN Management Protocol (TR-069 / TR-369 CWMP), tracking background telemetry leakage, and analyzing DNS exposure.
7. **Defensive Hardening and OpenWrt Migration:** Hardening stock configurations and transitioning proprietary consumer gateways to auditable, open-source firmware distributions.

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Why Reverse Engineering Wi-Fi Router Gateways Matters](#why-reverse-engineering-wi-fi-router-gateways-matters)
- [Threat Model and Attack Surface Analysis](#threat-model-and-attack-surface-analysis)
  - [1. Carrier Remote Management Channels (TR-069 / CWMP)](#1-carrier-remote-management-channels-tr-069--cwmp)
  - [2. Unencrypted DNS Query Interception](#2-unencrypted-dns-query-interception)
  - [3. Geolocation Triangulation via BSSID Harvesting](#3-geolocation-triangulation-via-bssid-harvesting)
  - [4. UPnP Dynamic Port Mapping and IGD Traversal](#4-upnp-dynamic-port-mapping-and-igd-traversal)
- [Phase 1: Hardware-Level Wi-Fi Router Reverse Engineering](#phase-1-hardware-level-wi-fi-router-reverse-engineering)
  - [Visual PCB Triage and Component Identification](#visual-pcb-triage-and-component-identification)
  - [UART Serial Pinout Detection and Console Access](#uart-serial-pinout-detection-and-console-access)
  - [Direct SPI NOR/NAND Flash Dumping via CH341A](#direct-spi-nornand-flash-dumping-via-ch341a)
- [Phase 2: Firmware Acquisition and File System Extraction](#phase-2-firmware-acquisition-and-file-system-extraction)
  - [Firmware Acquisition Strategies](#firmware-acquisition-strategies)
  - [Static Firmware Carving with Binwalk](#static-firmware-carving-with-binwalk)
  - [Manual File System Extraction: SquashFS and JFFS2](#manual-file-system-extraction-squashfs-and-jffs2)
- [Phase 3: Embedded Binary Disassembly and Vulnerability Research](#phase-3-embedded-binary-disassembly-and-vulnerability-research)
  - [Identifying Target Architecture (MIPS / ARM)](#identifying-target-architecture-mips--arm)
  - [Decompiling HTTP Daemons in Ghidra](#decompiling-http-daemons-in-ghidra)
  - [Auditing Common Vulnerability Patterns](#auditing-common-vulnerability-patterns)
- [Phase 4: Dynamic Emulation and Runtime Debugging](#phase-4-dynamic-emulation-and-runtime-debugging)
  - [User-Mode Emulation with QEMU](#user-mode-emulation-with-qemu)
  - [Full-System Firmware Emulation with Firmadyne](#full-system-firmware-emulation-with-firmadyne)
  - [System Call Tracing with strace and gdbserver](#system-call-tracing-with-strace-and-gdbserver)
- [Phase 5: Administrative Web API Reverse Engineering](#phase-5-administrative-web-api-reverse-engineering)
  - [Authentication Protocol Deconstruction](#authentication-protocol-deconstruction)
  - [Endpoint Mapping: JSON-RPC, ubus, and CGI](#endpoint-mapping-json-rpc-ubus-and-cgi)
  - [Automating API Queries Without Credential Exposure](#automating-api-queries-without-credential-exposure)
- [Phase 6: Carrier Management and Telemetry Auditing (TR-069)](#phase-6-carrier-management-and-telemetry-auditing-tr-069)
  - [Deconstructing TR-069 CWMP Operations](#deconstructing-tr-069-cwmp-operations)
  - [Empirical Telemetry Case Study](#empirical-telemetry-case-study)
- [Operational Workflows](#operational-workflows)
  - [Workflow 1: Read-Only Privacy and Telemetry Audit](#workflow-1-read-only-privacy-and-telemetry-audit)
  - [Workflow 2: Wireless Performance Optimization](#workflow-2-wireless-performance-optimization)
- [Security and Zero-Leakage Architecture](#security-and-zero-leakage-architecture)
  - [Local Keyring Credential Protection](#local-keyring-credential-protection)
  - [Deterministic Stream Masking (scripts/mask.py)](#deterministic-stream-masking-scriptsmaskpy)
- [Diagnostic Utilities Reference](#diagnostic-utilities-reference)
  - [scripts/dns-check.sh](#scriptsdns-checksh)
  - [scripts/mask.py](#scriptsmaskpy)
- [CPE Hardening and Remediation Protocol](#cpe-hardening-and-remediation-protocol)
- [Academic Research and Formal References](#academic-research-and-formal-references)
- [Supported Hardware and Firmware Ecosystems](#supported-hardware-and-firmware-ecosystems)
- [Technical Frequently Asked Questions](#technical-frequently-asked-questions)
- [Contribution Standards](#contribution-standards)
- [License and Legal Disclaimer](#license-and-legal-disclaimer)

---

## Why Reverse Engineering Wi-Fi Router Gateways Matters

Modern broadband Customer Premises Equipment (CPE) devices are specialized embedded computers typically operating BusyBox Linux on MIPS or ARM microarchitectures. Despite sitting at the perimeter of corporate and home networks, consumer routers suffer from widespread operational opacity:

1. **Undocumented Administrative APIs:** Web interfaces communicate with underlying daemons through undocumented HTTP POST endpoints, JSON-RPC endpoints, or legacy CGI routines. Reverse engineering Wi-Fi router web interfaces exposes these endpoints for automation and auditing.
2. **Hidden Carrier Telemetry Daemons:** Internet service providers routinely configure Auto-Configuration Server (ACS) daemons using the TR-069 / TR-369 protocol. These daemons maintain persistent connections to upstream ISP infrastructure, allowing remote configuration changes, telemetry extraction, and firmware updates without user knowledge.
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

## Phase 1: Hardware-Level Wi-Fi Router Reverse Engineering

When software and network probing interfaces are restricted, hardware-level reverse engineering provides direct access to the device's operating environment and persistent storage.

### Visual PCB Triage and Component Identification
1. Remove outer enclosure screws (often concealed beneath rubber feet or warranty labels).
2. Document all integrated circuit markings:
   - **System on Chip (SoC):** Identifies CPU architecture, core frequency, and integrated radios (e.g., MediaTek MT7621AT, Broadcom BCM4709, Qualcomm Atheros IPQ4019, Realtek RTL8197F).
   - **RAM Chip:** Determines memory bounds (e.g., Winbond, Nanya, or Samsung DDR2/DDR3 SDRAM).
   - **Flash Memory:** Identifies non-volatile storage type and capacity (SPI NOR flash like Winbond 25Q128 [16MB] or NAND flash like ESMT [128MB]).

### UART Serial Pinout Detection and Console Access
Embedded router motherboards almost universally provide a 3-pin or 4-pin UART header used by factory technicians for kernel debugging.

```
       [ Router Motherboard UART Header ]
         (1) VCC   (2) TX   (3) RX   (4) GND
          O         O        O        O
```

#### Locating UART Pins with a Multimeter:
1. **Locate Ground (GND):** Set multimeter to continuity mode. Touch one probe to the router's Ethernet metal shielding and test each pin. The pin that beeps is **GND**.
2. **Locate VCC (Power):** Set multimeter to DC voltage (20V). Power on the router. Measure voltage between GND and remaining pins. The pin reading steady **3.3V** or **5.0V** is **VCC** (do not connect this to your USB adapter).
3. **Locate Transmit (TX):** Monitor remaining pins during boot. The pin fluctuating rapidly between 2.0V and 3.3V while the CPU outputs bootloader text is **TX**.
4. **Locate Receive (RX):** The remaining non-voltage pin with slight resistance to ground is **RX**.

#### Connecting Serial Interface:
Connect a 3.3V USB-to-UART bridge (CP2102 or FT232RL):
- Bridge GND -> Router GND
- Bridge RX  -> Router TX
- Bridge TX  -> Router RX

Launch serial terminal session:
```bash
# Connect at standard baud rates (most commonly 115200 or 57600)
picocom -b 115200 /dev/ttyUSB0
# Or using screen
screen /dev/ttyUSB0 115200
```

Upon power cycling the router, the U-Boot bootloader output appears, typically culminating in an unauthenticated BusyBox root shell (`#`).

### Direct SPI NOR/NAND Flash Dumping via CH341A
When UART is disabled in production firmware (`console=null` in kernel arguments), physical flash extraction captures the complete binary state:

```bash
# Test chip detection via CH341A USB programmer and SOIC-8 clip
flashrom -p ch341a_spi

# Dump raw firmware partition to local file
flashrom -p ch341a_spi -r router_firmware_dump.bin

# Verify dump integrity by reading a second copy and comparing checksums
flashrom -p ch341a_spi -r router_firmware_dump2.bin
sha256sum router_firmware_dump.bin router_firmware_dump2.bin
```

---

## Phase 2: Firmware Acquisition and File System Extraction

Firmware extraction is the process of decomposing a monolithic firmware binary into individual kernel, bootloader, configuration, and root file system components.

### Firmware Acquisition Strategies
1. **Manufacturer Support Download:** Download stock updates (`.bin`, `.trx`, `.img`) directly from vendor portals.
2. **Network Interception of OTA Updates:** Sniff WAN traffic while triggering an over-the-air firmware update check via the router management UI.
3. **Hardware SPI Extraction:** Read directly from flash memory using hardware clips.

### Static Firmware Carving with Binwalk
[Binwalk](https://github.com/ReFirmLabs/binwalk) is the industry-standard tool for static firmware analysis:

```bash
# Scan firmware for signatures (SquashFS, U-Boot, LZMA, CramFS)
binwalk firmware.bin

# Example Output:
# DECIMAL       HEXADECIMAL     DESCRIPTION
# --------------------------------------------------------------------------------
# 0             0x0             TRX firmware header, little endian, image size: 16777216 bytes
# 28            0x1C            LZMA compressed data, properties: 0x5D, dictionary size: 67108864
# 1179648       0x120000        Squashfs filesystem, little endian, version 4.0, size: 14285714 bytes

# Recursively extract all identified components
binwalk -Me firmware.bin
```

### Manual File System Extraction: SquashFS and JFFS2
If automated Binwalk carving fails due to proprietary headers or non-standard compression offsets:

```bash
# 1. Manually carve SquashFS partition using dd
# Offset derived from binwalk scan (e.g., 0x120000 = 1179648)
dd if=firmware.bin of=rootfs.squashfs bs=1 skip=1179648

# 2. Extract using unsquashfs (or sasquatch for non-standard vendor LZMA)
unsquashfs rootfs.squashfs

# Extracted directory structure:
# squashfs-root/
# ├── bin/          (BusyBox symlinks, custom binaries)
# ├── etc/          (Configuration files, init scripts, shadow passwords)
# ├── sbin/         (Network daemons, iptables, ubus, netifd)
# ├── usr/
# │   └── sbin/     (httpd, dropbear, hostapd, dnsmasq, cwmp)
# └── www/          (Web management files, HTML, JavaScript, Lua, CGI)
```

---

## Phase 3: Embedded Binary Disassembly and Vulnerability Research

Once the file system is unpacked, the next phase involves static analysis of proprietary network daemons responsible for administration and routing.

### Identifying Target Architecture (MIPS / ARM)
Check binary characteristics using standard utilities:

```bash
file squashfs-root/usr/sbin/httpd
# Example: ELF 32-bit LSB executable, MIPS, MIPS32 version 1 (SYSV), dynamically linked

readelf -h squashfs-root/usr/sbin/httpd
```

### Decompiling HTTP Daemons in Ghidra
1. Launch Ghidra and create a new project.
2. Import the extracted web server binary (`httpd`, `uHTTPd`, `boa`, or `mini_httpd`).
3. Set language to:
   - For MIPS Little Endian: `MIPS:32:default:little` (e.g., MediaTek MT7621)
   - For MIPS Big Endian: `MIPS:32:default:big` (e.g., Atheros AR9344)
   - For ARM Little Endian: `ARM:32:default:little:v7`
4. Run auto-analysis with decompiler enabled.

### Auditing Common Vulnerability Patterns
Examine cross-references (`Xrefs`) to dangerous C functions:

| Function | Associated Risk | Reverse Engineering Focus |
| :--- | :--- | :--- |
| `system()`, `popen()` | Command Injection | Trace input parameters back to HTTP GET/POST variables without validation. |
| `strcpy()`, `sprintf()` | Buffer Overflow | Audit buffer allocations handling user-supplied cookies, hostnames, or passwords. |
| `nvram_get()`, `uci_get()` | Configuration Exposure | Identify hidden configuration parameters read at runtime. |
| `strcmp()`, `memcmp()` | Authentication Bypass | Audit hardcoded credentials and token comparison routines. |

---

## Phase 4: Dynamic Emulation and Runtime Debugging

Dynamic analysis allows security researchers to execute router binaries without requiring the physical device.

### User-Mode Emulation with QEMU
Using QEMU user-mode static binaries and `chroot`, individual MIPS/ARM programs can be executed on x86_64 host machines:

```bash
# 1. Install static QEMU binaries
sudo apt-get install qemu-user-static

# 2. Copy matching architecture emulator into rootfs
cp $(which qemu-mipsel-static) squashfs-root/usr/bin/

# 3. Chroot into rootfs and execute binary under emulation
sudo chroot squashfs-root /usr/bin/qemu-mipsel-static /usr/sbin/httpd -h
```

### Full-System Firmware Emulation with Firmadyne
[Firmadyne](https://github.com/firmadyne/firmadyne) and [EMBA](https://github.com/e-m-b-a/emba) automate full system emulation:

```bash
# Extract and identify architecture
./sources/extractor/extractor.py -b "Vendor" -sql "firmware.db" firmware.bin images/

# Emulate network interfaces and launch QEMU system instance
./scripts/run.sh 1
```

### System Call Tracing with strace and gdbserver
Trace system calls dynamically to observe runtime file access, socket bindings, and inter-process communications:

```bash
# Run binary with strace inside chroot
sudo chroot squashfs-root /usr/bin/qemu-mipsel-static -strace /usr/sbin/httpd

# Remote debugging via gdbserver
gdbserver :1234 /usr/sbin/httpd
# From host:
gdb-multiarch squashfs-root/usr/sbin/httpd -ex "target remote localhost:1234"
```

---

## Phase 5: Administrative Web API Reverse Engineering

Consumer gateways rarely supply public API documentation. Web reverse engineering maps internal administration interfaces for security evaluation and scripting.

### Authentication Protocol Deconstruction
Embedded routers commonly use multi-stage authentication schemes:

1. **MD5 / SHA-256 Challenge-Response:** The client sends an initial GET request to retrieve a dynamic challenge salt. The password hash is computed as `MD5(username + ":" + salt + ":" + password)`.
2. **PBKDF2 / AES Token Wrapping:** Modern routers encrypt payload forms client-side using JavaScript crypto libraries (`crypto-js`, `sjcl`) before transmission over HTTP.
3. **Session State Verification:** Requests require transient session cookies (`sysauth`, `session_id`) combined with anti-CSRF request tokens (`stok`, `csrf_token`).

### Endpoint Mapping: JSON-RPC, ubus, and CGI
Reverse engineering client-side JavaScript (`/www/js/*.js`) reveals internal dispatch endpoints:

```
+------------------------------------------------------------------------+
|                          Web Management Layer                          |
+------------------------------------------------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+-----------------------+                       +-----------------------+
|  CGI Script Handlers  |                       | JSON-RPC Dispatchers  |
|  - /cgi-bin/luci      |                       |  - /ubus              |
|  - /apply.cgi         |                       |  - /api/v1/status     |
|  - /router_status.cgi |                       |  - /data/wan_info.json|
+-----------------------+                       +-----------------------+
            |                                               |
            +-----------------------+-----------------------+
                                    |
                                    v
+------------------------------------------------------------------------+
|                   Underlying IPC / UCI Daemon Layer                    |
+------------------------------------------------------------------------+
```

### Automating API Queries Without Credential Exposure
Once endpoints are mapped, queries execute locally without exposing administrative credentials to remote systems:

```bash
# Example: Querying OpenWrt ubus interface for wireless association list
curl -s -X POST "http://192.168.1.1/ubus" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "call",
    "params": ["00000000000000000000000000000000", "iwinfo", "assoclist", {"device": "wlan0"}]
  }' | python3 scripts/mask.py
```

---

## Phase 6: Carrier Management and Telemetry Auditing (TR-069)

Carrier-deployed gateways frequently harbor background remote management daemons that operate outside user control.

### Deconstructing TR-069 CWMP Operations
The CPE WAN Management Protocol (TR-069 / TR-369) enables Auto-Configuration Servers (ACS) to manage customer devices via SOAP/XML messages over HTTP/HTTPS:

```
[ Carrier Auto-Configuration Server (ACS) ]
                     ^
                     | SOAP/XML over HTTP/HTTPS (Port 7547 or WAN tunnel)
                     v
[ CPE Embedded CWMP Daemon (cwmp / acs_client) ]
                     |
  -------------------+-------------------
  |                  |                  |
  v                  v                  v
[ Read WAN Config ] [ Dump ARP Cache ] [ Force Firmware Push ]
```

#### Key TR-069 Operations to Audit:
- **`GetParameterValues`:** Upstream carrier queries local parameters (SSID passphrases, serial numbers, connected host inventory).
- **`SetParameterValues`:** Carrier forces configuration overrides without local operator consent.
- **`Download` / `ScheduleDownload`:** Carrier initiates binary firmware replacements automatically.

### Empirical Telemetry Case Study
Verified telemetry parameters captured during an audit of a consumer optical broadband gateway:

| Parameter Key | Observed Value | Security Implication |
| :--- | :--- | :--- |
| **`InternetGatewayDevice.ManagementServer.URL`** | `http://acs.isp-domain.net:7547/` | Telemetry transported over unencrypted cleartext HTTP. |
| **`InternetGatewayDevice.ManagementServer.PeriodicInformInterval`** | `86400` (Seconds) | Device checks into remote carrier server every 24 hours. |
| **`InternetGatewayDevice.LANDevice.1.Hosts.HostNumberOfEntries`** | `29` | Device maintains historical inventory of 29 hardware clients. |
| **`InternetGatewayDevice.WANDevice.1.WANConnectionDevice.1.WANIPConnection.1.DNSServers`** | `103.x.x.1, 103.x.x.2` | 100% of local DNS lookups routed unencrypted through ISP resolvers. |

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

### Local Keyring Credential Protection
Administrative credentials are never pasted into chat contexts. Instead, credentials reside in host OS secure keyrings:
- **macOS:** `security add-generic-password -s "wifi-router-admin" -a "admin" -w "<password>"`
- **Windows:** `cmdkey /generic:wifi-router-admin /user:admin /pass:"<password>"`
- **Linux:** `secret-tool store --label="wifi-router-admin" service wifi-router-admin username admin`

### Deterministic Stream Masking (`scripts/mask.py`)
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

## Diagnostic Utilities Reference

### `scripts/dns-check.sh`
Queries authoritative Akamai verification endpoints to determine the outward-facing public resolver handling host queries:

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

### `scripts/mask.py`
A streaming filter designed to redact PII, hardware identifiers, and session tokens from diagnostic logs:

```bash
# Pipe any command output through the sanitizer
ipconfig /all | python3 scripts/mask.py

# Pipe router JSON status responses
curl -s http://192.168.1.1/api/status | python3 scripts/mask.py
```

---

## CPE Hardening and Remediation Protocol

Once the diagnostic baseline is established, apply systematic remediation:

1. **Encrypted DNS Configuration:** Deploy DNS-over-HTTPS (DoH) across endpoints (Android Private DNS, Windows 11 Encrypted DNS, iOS configuration profiles, Chrome/Firefox Secure DNS).
2. **MAC Address Randomization:** Enable private MAC addressing on client operating systems to prevent permanent client tracking.
3. **Geolocation Database Opt-Out (`_nomap`):** Append `_nomap` to all operational SSIDs to prevent Wi-Fi Positioning Systems from indexing your access point BSSID.
4. **Channel and Band Isolation:** Restrict 2.4 GHz channels strictly to non-overlapping channels **1, 6, or 11** at **20 MHz** width. Migrate high-bandwidth devices to **5 GHz** or **6 GHz** at 80 MHz channel widths.
5. **OpenWrt / Custom Firmware Flashing:** Where supported, replace proprietary OEM firmware with open-source distributions to achieve full transparency and control over background daemons.

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
No. The framework operates exclusively at the application and management layers of the router's existing administration console. It does not overwrite bootloaders, write to flash partitions, or install custom kernel packages without explicit manual operator configuration.

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
