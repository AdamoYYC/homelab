# Homelab Blueprint

## Concept
Build a fictional small Calgary company network ("DemoCorp Calgary" — placeholder
name) fully virtualized on Adam's PC. Every component is free: Windows Server
180-day evals, pfSense CE, Ubuntu, M365 trial tenant. Document each step publicly.

## Design

                    pfSense — firewall / router / VPN (2 GB RAM)
                    VLANs: staff / guest
                    |
        +-----------+-----------+
        |           |           |
      DC01        CLIENT      UBUNTU
      Win Srv     Win 10      (phase 4)
      AD/DNS/     domain      monitoring
      DHCP/GPO    joined
      (4 GB)      (4 GB)      (2 GB)

## Phase 1 — Core domain (start here)
- DC01: Windows Server 2022 Eval — AD DS, DNS, DHCP
- OU structure designed like a real SMB (departments, service accounts, groups)
- CLIENT01: Windows 10/11 Eval, domain-joined
- Group Policy: password policy, mapped drives, baseline security settings
- Docs: OU design rationale, GPO list, DNS/DHCP config, screenshots
- Interview value: AD, Group Policy, DNS, DHCP — his top keywords, now with "in my lab I…" stories

## Phase 2 — Network edge
- pfSense VM: firewall rules, staff/guest VLANs, WireGuard VPN for "remote worker"
- Docs: rule rationale, VPN setup, what each VLAN can reach
- Interview value: firewalls, VPN, VLANs, TCP/IP

## Phase 3 — Hybrid identity
- M365 trial tenant + Microsoft Entra ID Connect syncing DC01
- Docs: sync config, what hybrid identity solves, license assignment
- Interview value: Microsoft 365, Entra ID — directly matches his headline

## Phase 4 (optional) — Services & monitoring
- FS01: file server, NTFS + share permissions, backup routine
- Ubuntu VM: Zabbix or Wazuh monitoring, alerting on lab events
- Interview value: backup/disaster recovery, monitoring, documentation

## Public build log
- GitHub repo with docs/ per phase, network diagram, sanitized screenshots
- Each completed phase feeds a LinkedIn post
- Nothing sensitive: fictional company, lab-only credentials, no real data

## Rules
- $0 spend. Eval/trial/free-tier only.
- Everything documented as we go — docs are half the project.
- Every claim in the log must be true (same rule as the resume).
