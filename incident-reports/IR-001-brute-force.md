# Incident Report IR-001

## Incident ID
IR-001 (Sentinel Incident ID: 8097520)

## Severity
Medium

## Summary
A simulated SSH brute force attack was performed against `vm-web-01`, 
generating repeated failed authentication attempts (invalid usernames 
and failed key-based authentication) within a short time window. 
Detection 001 (Brute Force SSH) correctly identified the pattern and 
triggered a Sentinel incident.

## Detection
**Detection 001 — Brute Force SSH** (Sentinel Analytics Rule)

Query logic: counts failed authentication events (`Invalid user`, 
`Connection closed by authenticating user ... [preauth]`) grouped by host 
in 5-minute windows; triggers when count ≥ 5.

## Timeline
04:34:19 First failed attempt (invalid user / key auth failure)
04:35:59 Second failed attempt
04:38:16 Third failed attempt
04:39:37 Fourth failed attempt
04:39:44 Fifth and sixth failed attempts (threshold reached)
04:58:40 Sentinel Incident created (first scheduled rule run,
included 30-day lookback covering the above activity)


## Evidence
- `screenshots/sentinel/detection-001-incident.png` — Sentinel Incident 
  detail view showing entity graph, alert, and timeline
- Raw log sample: `attack-scenarios/01-brute-force/evidence/`

## Investigation

**Who?** Test performed by project owner (lab environment, not a genuine 
external attacker)

**What?** Repeated SSH authentication failures — invalid usernames and 
disabled key-authentication attempts

**When?** Sep 22, 2026, 04:34–04:39 AM (activity), 04:58 AM (detection)

**Where?** Target: `vm-web-01`. Source: primarily `127.0.0.1` (VM-internal 
test) and local test machine — not a real external threat actor

**Why?** Controlled simulation to validate Detection 001 end-to-end

**How?** SSH client commands forcing authentication failure (invalid 
username, disabled public key auth)

## MITRE ATT&CK
T1110 — Brute Force

## Impact
None (simulated, lab environment only). No successful unauthorized access 
occurred as a result of this test.

## Response
No automated response yet implemented (planned for Phase 9 — 
Automation 002: Block suspicious IP). Manual review confirmed the alert 
was a true positive against the intended test scenario.

## Root Cause
N/A — this was an intentional simulation, not an actual security incident.

## Remediation
N/A for this test. Notes for future hardening (Phase 10):
- Consider adding Fail2ban or similar to automatically block IPs after 
  repeated failures at the OS level, in addition to detection.
- Current detection has no source IP correlation in entity mapping — 
  future improvement to enrich alerts with source IP for better 
  investigation context.

## Lessons Learned
- VM's SSH-key-only configuration means classic "Failed password" log 
  signatures never appear — detection logic needed adjustment to match 
  actual observed failure messages (`Invalid user`, `Connection closed by 
  authenticating user ... [preauth]`).
- Sentinel's first rule run includes a 30-day lookback, which explains 
  the ~23-minute gap between "First activity" and "Creation time" in this 
  incident — worth noting so this isn't mistaken for a detection delay in 
  future reviews.