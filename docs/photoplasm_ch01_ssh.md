Photoplasm Quick Start Guide  ·  Chapter 1 — SSH Setup & VS Code Remote Development

# Chapter 1 — SSH Setup & VS Code Remote Development

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 1.0.0  ·  2026-04-28  ·  github.com/ericview-dev/photoplasm

---

## Overview

This chapter covers establishing a passwordless SSH connection from your Mac to the Raspberry Pi 5 (eyepi) and connecting VS Code for remote development. Once complete, you can edit scripts on the Pi directly from your Mac without ever copying files manually.

## Prerequisites

- Raspberry Pi 5 running Raspberry Pi OS (Bookworm)
- Mac with Terminal
- VS Code installed on Mac
- Pi and Mac on the same network

## 1.1 — Find the Pi's IP Address

On the Pi:

```bash
hostname -I
```

Note the IP address — e.g. `192.168.1.42`. Alternatively, if mDNS is configured:

```bash
ping raspberrypi.local
```

## 1.2 — Generate SSH Key on Mac

If you don't already have an SSH key:

```bash
ssh-keygen -t ed25519 -C "your@email.com"
```

Accept the default location (`~/.ssh/id_ed25519`). Leave passphrase blank for passwordless access.

## 1.3 — Copy Key to Pi

```bash
ssh-copy-id ericview@<PI_IP>
```

Enter the Pi password when prompted. This is the last time you'll need it.

## 1.4 — Create SSH Alias

Add a shortcut to `~/.ssh/config` on your Mac:

```
Host eyepi
    HostName <PI_IP>
    User ericview
    IdentityFile ~/.ssh/id_ed25519
```

Now connect with simply:

```bash
ssh eyepi
```

## 1.5 — Test Passwordless SSH

```bash
ssh eyepi "hostname && python3 --version"
```

Should return the Pi hostname and Python version without prompting for a password.

## 1.6 — Install VS Code Remote SSH Extension

In VS Code:

- Open Extensions (Cmd+Shift+X)
- Search Remote - SSH
- Install the Microsoft extension

## 1.7 — Connect VS Code to Pi

- Press Cmd+Shift+P → type Remote-SSH: Connect to Host
- Select eyepi
- VS Code opens a new window connected to the Pi
- Open folder: `/home/ericview/photoplasm`

Install the Python extension when prompted — this adds syntax highlighting and autocomplete for Pi-side scripts.

## 1.8 — Verify End-to-End

Open the VS Code terminal (Ctrl+\`) — it opens directly on the Pi. Run:

```bash
pwd
# /home/ericview/photoplasm

python3 --version
# Python 3.11.x
```

You are now editing Pi files from your Mac with full IDE support.

## Known Issues & Fixes

| Error | Cause | Fix |
|---|---|---|
| Permission denied (publickey) | Key not copied to Pi | Run `ssh-copy-id` again |
| Host key verification failed | Pi IP changed | Remove old entry: `ssh-keygen -R <PI_IP>` |
| Connection timed out | Pi not on network | Check Pi is powered and on same WiFi/LAN |
| VS Code stuck connecting | Remote SSH extension issue | Reload window: Cmd+Shift+P → Reload Window |

## Summary

| Step | Command | Result |
|---|---|---|
| Generate key | `ssh-keygen -t ed25519` | Key pair created |
| Copy to Pi | `ssh-copy-id ericview@PI_IP` | Passwordless auth enabled |
| SSH alias | Edit `~/.ssh/config` | `ssh eyepi` works |
| VS Code | Remote-SSH extension | Full IDE on Pi |

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v1.0.0  ·  2026-04-28  ·  published
