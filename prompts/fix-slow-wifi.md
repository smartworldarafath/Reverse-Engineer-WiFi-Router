# Fix Slow Wi-Fi Prompt

Diagnose and optimize your Wi-Fi router settings to resolve speed and lag issues.

---

## Instructions

Paste the prompt below into Claude Code while your computer is connected to your home Wi-Fi network.

```markdown
My Wi-Fi is slow and laggy. Please help me diagnose and fix it using my router's local admin API.
I have attached a photo of my router (with the password sticker covered).

Please follow these safety rules:
1. Work locally on my network without password guessing or exploits.
2. If router credentials are required, provide a terminal command to store the password in my local system keystore. Never prompt for or display passwords in chat.
3. Mask sensitive information (public IP, MAC addresses, serial numbers, SSID).
4. Do NOT change any settings automatically. Always explain the diagnosis and wait for my explicit confirmation before applying any changes.

Please:
1. Identify the router model from the photo and locate its local admin API.
2. Diagnose why the connection is slow (interference, crowded channels, 2.4 GHz vs 5 GHz/6 GHz band allocation, channel width, device saturation).
3. Propose optimal adjustments and, upon my approval, apply the changes to fix my Wi-Fi.
```

## Diagnostics Covered

- **Band Selection**: Checking whether high-bandwidth devices are stuck on congested 2.4 GHz instead of 5 GHz / 6 GHz.
- **Channel Congestion**: Scanning neighboring access points to find clean non-overlapping channels (1, 6, 11 on 2.4 GHz, or clean 5 GHz channels).
- **Channel Width**: Verifying if channel width is capped (e.g. 20 MHz vs 40/80/160 MHz).
- **Client Bandwidth Hogs**: Inspecting active device throughput to catch background bandwidth consumers.
- **WAN Port Negotiation**: Verifying Ethernet link speed between modem and router (100 Mbps fast ethernet vs 1000 Mbps gigabit).
