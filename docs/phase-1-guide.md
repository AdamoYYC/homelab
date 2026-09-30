# Phase 1 — Core Domain: Build Guide

Goal: a working Active Directory domain on a virtual lab LAN, with a
domain-joined client and Group Policy applied. This is the foundation every
later phase builds on.

## 0. Downloads (free, ~11 GB total)

1. Windows Server 2022 Evaluation (180-day trial)
   https://www.microsoft.com/en-us/evalcenter/download-windows-server-2022
   Register with a Microsoft account, choose ISO, 64-bit, English.
2. Windows 11 Enterprise Evaluation (90-day trial)
   https://www.microsoft.com/evalcenter/download-windows-11-enterprise
   Same process. This is the domain client.

Stash both ISOs somewhere permanent (e.g. D:\ISOs\) — you'll reuse them.

## 1. VMware virtual networks

Workstation Pro → Edit → Virtual Network Editor (run as Administrator):

- VMnet8, NAT, default subnet, DHCP on — pfSense WAN (Phase 2)
- VMnet2, Host-only, 192.168.10.0/24, DHCP OFF — Lab LAN (DC01 is the DHCP server)
- VMnet3, Host-only, 192.168.20.0/24, DHCP off — Guest VLAN (Phase 2)

Uncheck "Use local DHCP service" on VMnet2 — the domain controller handles DHCP.

## 2. DC01 — domain controller

New VM: 2 vCPU, 4 GB RAM, 60 GB disk (thin), 1 NIC on VMnet2.
Install Windows Server 2022, choose Desktop Experience (GUI).

Post-install:
- Rename to DC01, static IP 192.168.10.10/24, gateway 192.168.10.1
  (pfSense LAN IP in Phase 2 — no gateway needed yet), DNS 127.0.0.1
- Server Manager → Add Roles: AD DS, DNS, DHCP
- Promote to domain controller: new forest, root domain homelab.local,
  DSRM password recorded somewhere safe (lab-only; the public log uses a
  placeholder like P@ssw0rd-lab — never a real password)
- DHCP scope: 192.168.10.100–192.168.10.200, router 192.168.10.1,
  DNS 192.168.10.10, authorize the DHCP server in AD

## 3. OU structure + accounts

In Active Directory Users and Computers, build it like a real SMB:

homelab.local
- _Admin (service/admin accounts)
- Calgary-HQ
  - IT
  - Sales
  - Operations
- _ServiceAccounts

- Create 3–4 test users across departments, 2 security groups
  (GG-IT-Admins, GG-Sales), one service account
- This OU design is deliberate — Group Policy targets OUs, and a clean
  structure is exactly what interviewers ask about

## 4. CLIENT01 — domain workstation

New VM: 2 vCPU, 4 GB RAM, 60 GB disk, 1 NIC on VMnet2.
Install Windows 11 Enterprise Eval → get DHCP address from DC01 →
join homelab.local → reboot → log in as a domain test user.

## 5. Group Policy (the part that impresses)

In Group Policy Management Console on DC01:

1. Password policy — link at domain level: min length 12, complexity on
2. Mapped drive — GPO on Calgary-HQ: map S: to \\DC01\Shared
   (create the share on DC01 first, NTFS + share permissions for GG groups)
3. Baseline hardening — e.g. disable guest account, rename Administrator,
   screensaver lock after 10 min idle

On CLIENT01: gpupdate /force, then verify — mapped drive appears,
gpresult /r shows the policies applied.

## 6. Verification checklist

- CLIENT01 gets 192.168.10.x from DC01's DHCP
- nslookup homelab.local on CLIENT01 resolves to 192.168.10.10
- Domain login works for a test user
- gpresult /r shows all three GPOs applied
- dcdiag on DC01 passes (note any warnings honestly in the log)

## 7. Document as you go (this is half the project)

For the public build log, capture per step: what you did, why (one line),
a screenshot, and anything that went wrong + the fix. Notes on failures are
more valuable than clean runs — they prove real troubleshooting.

## RAM budget (16 GB host — be disciplined)

- Host Win11: ~4 GB, always
- DC01: 4 GB, Phase 1+
- CLIENT01: 4 GB, Phase 1+
- pfSense: 2 GB, Phase 2+

Rule: max 3 lab VMs powered on at once. Suspend or power off whatever the
current phase doesn't need. Phase 3 (Entra Connect) installs on DC01 itself —
no extra VM. Phase 4 monitoring VM (2 GB) replaces CLIENT01's slot when you
get there.
