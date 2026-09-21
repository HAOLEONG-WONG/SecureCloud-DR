# Brute Force — Preliminary Log Sample (Phase 3)

This sample was generated during Phase 3 application testing to validate 
the authentication logging format before formal attack simulation (Phase 7).

6 consecutive FAILURE attempts followed by 1 SUCCESS — this pattern will 
be the basis for Detection 001 (Brute Force, MITRE T1110) in Phase 6.

# Attack Scenario 01 — SSH Brute Force

## Scenario ID
AS-001

## Title
SSH Brute Force Authentication Attempt

## Objective
Demonstrate detection of repeated failed SSH authentication attempts 
against a single host, simulating a brute force credential attack.

## Threat Model
Maps to `docs/04-threat-model.md` — External attacker attempting to gain 
initial access via SSH credential guessing.

## Prerequisites
- Target VM (`vm-web-01`) reachable via SSH
- Log pipeline confirmed working (Azure Monitor Agent → Log Analytics → Sentinel)

## Environment
- Target: `vm-web-01` (Ubuntu 24.04 LTS)
- Attack origin: Local machine / VM-internal test (lab-safe simulation)

## Attack Simulation
Simulated failed authentication attempts using invalid usernames and 
disabled key authentication, generating repeated SSH failures within a 
short time window:
```bash
ssh nonexistentuser@localhost
ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password azureuser@<target-ip>
```

## Expected Telemetry
`Syslog` table (Facility: auth/authpriv), messages containing:
- `Invalid user <username> from <ip>`
- `Connection closed by authenticating user <username> ... [preauth]`

## Detection
**Detection 001 — Brute Force SSH** (Sentinel Analytics Rule)
```kql
Syslog
| where Facility in ("auth", "authpriv")
| where SyslogMessage has "Invalid user" 
    or SyslogMessage has "Connection closed by authenticating user"
    or SyslogMessage has "Connection closed by invalid user"
| summarize FailedAttempts = count() by Computer, bin(TimeGenerated, 5m)
| where FailedAttempts >= 5
```
Threshold: 5+ failures within 5 minutes.

## MITRE ATT&CK Mapping
- T1110 — Brute Force

## Response
(To be implemented in Phase 9 — Automation 002: Block suspicious IP)

## Validation
[Pending — awaiting first incident trigger to confirm end-to-end detection]

## Lessons Learned
- VM is configured for SSH key-only authentication (no password auth 
  enabled), so classic "Failed password" log messages never occur. 
  Detection logic had to be adjusted to match the actual failure patterns 
  this configuration produces (`Invalid user`, `Connection closed by 
  authenticating user ... [preauth]`) rather than assuming generic brute 
  force log signatures.
- Verified raw log data in Sentinel before writing detection logic — 
  confirmed actual message format rather than assuming standard "Failed 
  password" text.

## Limitations
- Test was internally simulated (from within/near the lab environment), 
  not from a genuinely external, unknown attacker IP.
- Detection does not currently capture source IP for correlation (entity 
  mapping limited to Device/Computer).


  