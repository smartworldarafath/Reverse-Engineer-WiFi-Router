# Privacy Check Prompt

Run a privacy and security audit on your home Wi-Fi router.

---

## Instructions

Paste the prompt below into Claude Code while your computer is connected to your home Wi-Fi network.

```markdown
I want to run a privacy check on my home Wi-Fi router. 
I have attached a photo of my router (with the password sticker covered).

Please perform a read-only privacy audit following these safety rules:
1. Operate strictly on my local network. Do not attempt external scans, password guessing, or exploits.
2. Never ask me to type my admin password in the chat. If authentication is needed, give me a single terminal command to save it to my local system password store.
3. Mask sensitive data (public IPs, second half of MAC addresses, serial numbers, and Wi-Fi names) in all outputs.

Please analyze the router photo, deduce the administration interface/API, inspect my router, and answer:
- What does my router know about me? (connected devices history, logs, tracked traffic)
- What can my ISP / internet provider see and reach? (TR-069 / remote management channels, plain-text DNS lookups, firmware update control)
- What specific steps should I take to fix and lock down my privacy?
```

## How It Works

1. **Identification**: Claude analyzes the physical router photo to identify the manufacturer, exact model, hardware version, and typical admin interface layout.
2. **Local Gateway Discovery**: Claude identifies your local gateway IP (e.g., `192.168.1.1`) and maps the endpoints.
3. **Audit Execution**: Claude queries the local router API to check:
   - Device history table (all devices that have ever connected).
   - Remote management configuration (TR-069, CWMP, ACS settings).
   - Upstream DNS servers and plain-text lookup leakage.
   - Firmware age and update control.
4. **Actionable Report**: You receive a clear summary with concrete remediation steps (Encrypted DNS, `_nomap`, Private Wi-Fi MACs, password rotation).
