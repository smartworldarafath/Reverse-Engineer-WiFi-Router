<div align="center">

# Reverse-Engineer Wi-Fi Router

**Autonomous AI Skill & Security Diagnostic Toolkit for Home Wi-Fi Routers**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-7A58EC.svg)](SKILL.md)
[![Security: Local Audit Only](https://img.shields.io/badge/Security-Local%20Audit%20Only-brightgreen.svg)](#-core-safety--zero-leak-rules)
[![GitHub Stars](https://img.shields.io/github/stars/smartworldarafath/Reverse-Engineer-WiFi-Router?style=social)](https://github.com/smartworldarafath/Reverse-Engineer-WiFi-Router/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/smartworldarafath/Reverse-Engineer-WiFi-Router?style=social)](https://github.com/smartworldarafath/Reverse-Engineer-WiFi-Router/network/members)

<p align="center">
  Send <b>Claude Code</b> one photo of your home Wi-Fi router. It works out the router's hidden admin API by itself, audits your privacy, and optimizes slow Wi-Fi—safely, locally, and with zero password guessing.
</p>

</div>

---

## ?? Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [What It Discovered on a Real Router](#-what-it-discovered-on-a-real-router)
- [Quick Start & Installation](#-quick-start--installation)
  - [Method 1: Install as a Claude Code Skill](#method-1-install-as-a-claude-code-skill)
  - [Method 2: Standalone Copy-Paste Prompts](#method-2-standalone-copy-paste-prompts)
- [Core Safety & Zero-Leak Rules](#-core-safety--zero-leak-rules)
- [How to Fix & Lock Down Your Router Privacy](#-how-to-fix--lock-down-your-router-privacy)
- [Scientific Research & Empirical Evidence](#-scientific-research--empirical-evidence)
- [Repository Structure & Tooling](#-repository-structure--tooling)
- [Frequently Asked Questions (FAQ)](#-frequently-asked-questions-faq)
- [Contributing & Community](#-contributing--community)
- [License](#-license)

---

## ?? Overview

**Reverse-Engineer Wi-Fi Router** (`Reverse-Engineer-WiFi-Router`) is an open-source security audit, diagnostics, and optimization framework designed for home network administrators, privacy advocates, and security enthusiasts. 

Instead of searching through obscure manufacturer manuals, deciphering complex web consoles, or guessing network parameters, this AI skill inspects the physical router from a photo, identifies the model and gateway architecture, maps internal administration endpoints (REST, CGI, JSON, LuCI), and guides you through:

1. **Privacy Audit (Read-Only):** Discovering everything your router logs, device histories, and what your Internet Service Provider (ISP) can see and reach.
2. **Wi-Fi Diagnostics & Troubleshooting:** Identifying interference, congestion, and band bottlenecks, and optimizing your network with your explicit approval.

---

## ? Key Features

- **Automated Gateway & API Discovery:** Deduces the administration web panel, login mechanisms (tokens, hashes, sessions), and internal data paths from the router photo and local subnet.
- **Privacy & ISP Surveillance Audit:** Checks for hidden TR-069/CWMP remote-management tunnels, plain-text DNS leak paths, and telemetry reporting.
- **Speed & Interference Optimization:** Scans 2.4 GHz vs 5 GHz channels, detects neighboring Wi-Fi overlap, identifies bandwidth-hogging clients, and tunes channel width.
- **Zero Exploits & Non-Destructive:** No brute-forcing, no dictionary attacks, no CVE exploits, and no external port scanning.
- **Strict Credential Privacy:** Admin passwords never enter chat logs. Saved securely to native OS keystores (macOS Keychain, Windows Credential Manager, Linux Secret-Tool).
- **Automated PII Sanitization:** Built-in masking scripts scrub public IPs, MAC address halves, serial numbers, and Wi-Fi SSIDs from terminal output.

---

## ?? What It Discovered on a Real Router

Running this audit on a standard consumer ISP-provided router revealed:

- ?? **29 Remembered Devices:** The router preserved a persistent log of 29 devices that had ever connected to the Wi-Fi network.
- ?? **ISP Remote Management Tunnel:** The primary WAN connection was named `TR069_INTERNET`—an active remote management backchannel managed by the provider that cannot be disabled from standard UI settings.
- ?? **Locked Firmware Updates:** No manual update button existed; the router ran outdated software with firmware changes restricted entirely to the ISP.
- ?? **Plain-Text DNS Lookups:** Every visited domain name was queried in unencrypted plain text through the provider's default resolver.
- ?? **Background TV Box Telemetry:** An ISP application on a connected Android TV box continued transmitting data while the television was in sleep mode.
- ?? **Timestamped Audit Trails:** Every user login and router configuration change was logged down to the exact minute.

---

## ?? Quick Start & Installation

### Method 1: Install as a Claude Code Skill

Clone this repository into your local Claude Code skills directory:

```bash
git clone https://github.com/smartworldarafath/Reverse-Engineer-WiFi-Router.git ~/.claude/skills/reverse-engineer-wifi-router
```

1. Connect your computer to your home Wi-Fi network.
2. Open **Claude Code**, attach a clear photo of your router (be sure to cover any password or PIN stickers), and ask:
   - `"what does my router know about me?"` *(Runs Job 1: Privacy Check)*
   - `"my Wi-Fi is slow, fix it"` *(Runs Job 2: Performance Diagnostic & Optimization)*

### Method 2: Standalone Copy-Paste Prompts

If you prefer not to install the skill globally, paste either of the standalone prompt templates directly into your AI assistant session:

- **[prompts/privacy-check.md](prompts/privacy-check.md)**: Instant read-only privacy, DNS leak, and TR-069 audit.
- **[prompts/fix-slow-wifi.md](prompts/fix-slow-wifi.md)**: Speed diagnostic, channel tuning, and controlled router optimization.

---

## ??? Core Safety & Zero-Leak Rules

This project enforces strict operational constraints to ensure network safety and data privacy:

| Security Rule | Implementation Detail |
| :--- | :--- |
| **Local Subnet Only** | Operates strictly within local IP ranges (`192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`). No external port scans or WAN packets. |
| **No Password Guessing** | Never uses brute-force scripts, telnet/ssh dictionary attacks, or vulnerability exploits. |
| **Zero Credential Chat Leaks** | Generates a single terminal command to save credentials into your system's secure keystore. Credentials are never sent into chat. |
| **Data Masking (`mask.py`)** | Automatically redacts public IPs, device-identifying MAC octets, serial numbers, and SSIDs from terminal output before display. |
| **Explicit Consent for Changes** | Privacy audits are **100% read-only**. Settings are modified only after you explicitly type `yes`. |

---

## ?? How to Fix & Lock Down Your Router Privacy

Following the diagnostic audit, apply these 5 key hardening steps:

1. **Change Default Admin Password:** Never leave the factory-printed password on your router's sticker active.
2. **Enable Encrypted DNS (DoH / DoT):** Prevent your ISP from logging your website lookups:
   - **Android:** *Settings > Network & internet > Private DNS* ([Google Guide](https://support.google.com/android/answer/9654714))
   - **Google Chrome:** *Settings > Privacy & security > Security > Use secure DNS* ([Chrome Guide](https://support.google.com/chrome/answer/10468685))
   - **Mozilla Firefox:** *Settings > Privacy & Security > DNS over HTTPS* ([Firefox Guide](https://support.mozilla.org/kb/dns-over-https))
   - **Windows 11:** Enable DNS encryption in network adapter properties ([Microsoft Guide](https://learn.microsoft.com/windows-server/networking/dns/doh-client-support))
   - **Apple iOS / macOS:** Use Cloudflare's free [1.1.1.1 App](https://one.one.one.one) in DNS-only mode.
3. **Turn on Private Wi-Fi Addresses:** Enable randomized MAC addressing on mobile devices to prevent hardware tracking across routers.
4. **Append `_nomap` to Wi-Fi SSID:** Prevent global location databases ([Apple](https://support.apple.com/en-us/102515) and [Google](https://support.google.com/maps/answer/1725632)) from cataloging your home coordinates.
5. **Rotate Wi-Fi Passwords:** Disconnect stale or unrecognized historical devices from your network.

> *Note: Encrypted DNS hides domain queries, but does not conceal the destination IP address. For total traffic encryption, use a verified VPN.*

---

## ?? Scientific Research & Empirical Evidence

The privacy and remote management risks audited by this tool are grounded in peer-reviewed academic security research:

- **Broadband TR-069 Protocol Vulnerabilities:**  
  *Nearly 1 billion home networking devices worldwide operate with an active TR-069 remote-management channel accessible to upstream telecom operators.*  
  Reference: Hils & Böhme, University of Innsbruck, *"Watching the Weak Link into Your Home"*, ACNS 2020, [arXiv:2001.02564](https://arxiv.org/abs/2001.02564).

- **Global Wi-Fi Positioning Surveillance:**  
  *Researchers extracted geolocation data for over 2 billion Wi-Fi routers from publicly accessible positioning APIs, capable of locating individual homes with meter accuracy.*  
  Reference: Rye & Levin, University of Maryland, *"Surveilling the Masses with Wi-Fi-Based Positioning Systems"*, 2024, [arXiv:2405.14975](https://arxiv.org/abs/2405.14975).

---

## ?? Repository Structure & Tooling

```plaintext
Reverse-Engineer-WiFi-Router/
+-- SKILL.md                 # Complete agent instructions and orchestration workflows
+-- README.md                # Project documentation, research background & guide
+-- LICENSE                  # Open-source MIT License
+-- prompts/
¦   +-- privacy-check.md     # Standalone copy-paste prompt for read-only privacy audit
¦   +-- fix-slow-wifi.md     # Standalone copy-paste prompt for speed & channel diagnostics
+-- scripts/
    +-- dns-check.sh         # Shell utility to verify DNS resolver ownership and leaks
    +-- mask.py              # Python PII sanitizer for IPs, MACs, serials, and SSIDs
```

### Script Usage

- **Check Current DNS Resolver:**
  ```bash
  ./scripts/dns-check.sh
  ```
- **Mask Sensitive Output:**
  ```bash
  some-diagnostic-command | python3 scripts/mask.py
  ```

---

## ? Frequently Asked Questions (FAQ)

<details>
<summary><b>1. How does Reverse-Engineer Wi-Fi Router figure out my router's API from a photo?</b></summary>
<p>
The vision model identifies the exact manufacturer, model number, hardware revision, and default firmware UI (such as OpenWrt, Broadcom, MediaTek, or proprietary ISP skins) from the physical design, casing, and logos. It then queries standard local gateway routes and maps frontend JavaScript, CGI, or JSON endpoints used by that web interface.
</p>
</details>

<details>
<summary><b>2. Does this skill require root access, flashing custom firmware, or voiding warranties?</b></summary>
<p>
No. The tool operates purely through standard local network communication using the router's existing web administration interface and network protocols. It does not flash firmware, alter partitions, or void warranties.
</p>
</details>

<details>
<summary><b>3. Is my router password sent to AI servers or recorded in chat?</b></summary>
<p>
Never. The skill strictly forbids typing admin passwords into chat. Instead, it provides a command to save the password locally into your operating system's native password manager (macOS Keychain, Windows Credential Manager, or Linux Secret-Tool).
</p>
</details>

<details>
<summary><b>4. Which routers are supported?</b></summary>
<p>
Virtually any Wi-Fi router or ISP gateway with a browser-accessible administration console (TP-Link, Netgear, ASUS, Huawei, ZTE, D-Link, Linksys, Technicolor, Sagemcom, etc.). App-only routers (like Google Nest or eero) receive a local network-level audit.
</p>
</details>

<details>
<summary><b>5. Can this tool damage or brick my Wi-Fi router?</b></summary>
<p>
No. The privacy check is completely read-only. In the performance optimization workflow, only standard Wi-Fi configuration parameters (channel, channel width, band steering) can be adjusted, and every modification requires your explicit confirmation before execution.
</p>
</details>

---

## ?? Contributing & Community

Contributions, issue reports, and router API mappings are welcome!

1. Fork the repository: `https://github.com/smartworldarafath/Reverse-Engineer-WiFi-Router`
2. Create a feature branch: `git checkout -b feature/new-router-mapping`
3. Commit your changes: `git commit -m "feat: add API mapping for Archer AX55"`
4. Push to branch: `git push origin feature/new-router-mapping`
5. Open a Pull Request.

If this project helped you secure and optimize your home network, please **Star (?)** the repository to support continued open-source development!

---

## ?? License

This project is licensed under the **[MIT License](LICENSE)** &mdash; free for personal and educational use.
