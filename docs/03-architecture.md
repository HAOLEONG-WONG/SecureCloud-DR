# Architecture — Phase 1 Progress

## Resources Created So Far
- Resource Group: `rg-securecloud-dr-lab`
- Virtual Network: `vnet-securecloud-dr` (10.0.0.0/16), region: Malaysia West
- Subnet: `snet-web` (10.0.0.0/24)
- Network Security Group: `nsg-web` — inbound rule allows SSH (port 22) only from my current IP

## Notes
- Region constrained to Azure for Students allowed list: uaenorth, eastasia, malaysiawest, indiasouthcentral, indonesiacentral
- Chose Malaysia West for lowest latency

- Virtual Machine: `vm-web-01`
  - Size: Standard B2ats_v2 (1 vCPU... wait, 2 vCPU / 1 GiB RAM)
  - OS: Ubuntu Server 24.04 LTS
  - Auth: SSH public key (RSA), no password login
  - Public inbound ports: None (relies on custom NSG instead of Azure defaults)
  - Disk: Standard SSD (Standard_LRS)
  - Region: Malaysia West (subscription-restricted allowed list)
  
  ## Phase 3 — Web Application Deployed

- Nginx (reverse proxy, port 80, public)
- Gunicorn (WSGI server, port 5000, internal only — bound to 127.0.0.1)
- Flask app (`~/webapp/app.py`), running as systemd service `webapp.service`
- NSG updated: added `Allow-HTTP-Any` rule (port 80, source: Any)

Architecture: Internet → NSG → Nginx (80) → Gunicorn (127.0.0.1:5000) → Flask

## Phase 3 — Login Feature Added

- SQLite database (`users.db`) with a `users` table, one test user seeded
- `/login` route added to Flask app: accepts POST with username/password
- **Intentional vulnerability:** SQL query built via f-string concatenation, 
  not parameterized — deliberately left as an attack surface for Phase 7 
  (SQL Injection simulation)
- Correct/secure version for future remediation reference:
  `c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))`

### Troubleshooting notes (kept for reference)
- Files initially created in wrong directory (`~` instead of `~/webapp`) — 
  systemd service reads from `~/webapp`, so changes weren't reflected until 
  corrected
- Database filename mismatch (`user.db` vs `users.db`) caused a fresh empty 
  DB to be auto-created by SQLite, leading to a 500 error (missing table)
- Multi-line heredoc (`cat > file << 'EOF'`) proved more reliable than nano 
  for pasting code without indentation corruption

## Phase 3 — Authentication Logging Added

- Structured JSON logging added to `/login` route
- Log file: `~/webapp/auth.log`
- Fields captured: timestamp (UTC, ISO 8601), event_type, username, result (SUCCESS/FAILURE), source_ip
- Purpose: prepares telemetry for Phase 4 (Azure Monitor → Log Analytics ingestion) 
  and Phase 6 Detection 001 (Brute Force — repeated authentication failures)

## Phase 4 — Centralized Logging (Azure Monitor → Log Analytics)

### Components Deployed
- **Log Analytics Workspace:** `law-securecloud-dr` (Malaysia West, 30-day retention)
- **Azure Monitor Agent:** installed on `vm-web-01`
- **Data Collection Rule:** `dcr-vm-web-01-logs`
  - Data source: Linux Syslog
  - Facilities collected: `LOG_AUTH`, `LOG_AUTHPRIV` (minimum level: `LOG_INFO`)
  - Destination: `law-securecloud-dr`

### Verification
Confirmed SSH authentication events (`sshd`, `systemd-logind`) successfully 
ingested into the `Syslog` table, including source IP, session open/close 
events, and public key authentication results.

### Query used for verification
```kql
Syslog
| where Facility in ("auth", "authpriv")
| order by TimeGenerated desc
| take 20
```

### Design Note
Data Collection Rule facility filtering controls collection scope, but does 
not fully eliminate baseline system Syslog noise (e.g., `systemd`, 
`MetricsExtension`). Filtering to auth-relevant events is instead handled 
at the query layer (`where Facility in (...)`) rather than the ingestion 
layer — consistent with typical SIEM workflow where raw ingestion is broad 
and precision is applied through detection queries.

### Cost
Estimated monthly data ingestion cost: US$0.00 (well under the 5GB/day 
free tier threshold given current log volume).

### Security Note
Real public IP addresses observed in Syslog data (e.g., SSH source IP) are 
kept out of publicly committed evidence files. Sample evidence documents 
use localhost (127.0.0.1) or redacted IPs instead of real addresses.

## Phase 2 — Terraform (Infrastructure as Code)

### Approach
Existing manually-created resources were migrated into Terraform management 
using `terraform import`, rather than destroying and recreating them — 
preserving the working VM, application, and log data built in Phases 3-4.

### Resources Imported
- `azurerm_resource_group.main` → `rg-securecloud-dr-lab`
- `azurerm_virtual_network.main` → `vnet-securecloud-dr`
- `azurerm_subnet.web` → `snet-web`
- `azurerm_network_security_group.web` → `nsg-web`
- `azurerm_network_security_rule.allow_ssh` → `Allow-SSH-MyIP`
- `azurerm_network_security_rule.allow_http` → `Allow-HTTP-Any`

### Still Pending
- Virtual Machine (`vm-web-01`) — not yet imported
- Storage Account (`stsecuredr01`) — not yet imported

### Security Practice
The SSH-allowed source IP is a variable (`var.my_ip_address`), not a 
hardcoded value, and is marked `sensitive = true` in `variables.tf`. The 
actual IP value is stored in `terraform.tfvars`, which is excluded via 
`.gitignore` and never committed to the public repository.

### Lessons Learned
- `terraform plan` showing "destroy and recreate" for a resource (e.g., 
  subnet) usually indicates a missing attribute in the config that doesn't 
  match Azure's actual default — resolved by explicitly setting 
  `default_outbound_access_enabled = false` to match the real resource.
- Terraform commands must be run from the local machine (where Terraform 
  is installed), not from within the SSH session to the Azure VM — these 
  are two separate environments with separate toolchains.

## Phase 2 — Terraform (continued): VM, Network Interface, Public IP

### Resources Imported
- `azurerm_network_interface.vm_web_01` → `vm-web-01462`
- `azurerm_linux_virtual_machine.web` → `vm-web-01`
- `azurerm_public_ip.vm_web_01` → `vm-web-01-ip`

### Issues Resolved
- **SSH public key generation**: Azure only provides the private key (`.pem`) 
  on VM creation; the public key was derived locally using 
  `ssh-keygen -y -f vm-web-01_key.pem`, required by Terraform's 
  `admin_ssh_key` attribute.
- **admin_ssh_key drift**: Azure appends `generated-by-azure` to the stored 
  public key, causing a permanent diff against the locally-derived key. 
  Resolved with `lifecycle { ignore_changes = [admin_ssh_key] }` — a 
  standard Terraform pattern for platform-generated metadata that should 
  not trigger resource replacement.
- **Case sensitivity**: `source_image_reference.publisher` required lowercase 
  `"canonical"` to match Azure's stored value (was `"Canonical"`).
- **Public IP SKU**: Standard SKU requires `allocation_method = "Static"` 
  (not `"Dynamic"`) — a hard Azure platform constraint.
- Explicitly declared `identity`, `boot_diagnostics`, and 
  `additional_capabilities` blocks to prevent Terraform from disabling 
  these features on apply (omitting them would have set them to null/disabled).

### Multi-IP SSH Access
Migrated from a single `source_address_prefix` to `source_address_prefixes` 
(list) to support SSH access from multiple trusted networks (e.g., home, 
mobile hotspot) without manually editing the NSG rule each time the IP changes.

### Status
All core infrastructure (Resource Group, VNet, Subnet, NSG + rules, VM, 
NIC, Public IP) is now fully managed by Terraform. `terraform plan` returns 
"No changes" — configuration matches real infrastructure exactly.

### Still Pending
- Storage Account (`stsecuredr01`) — not yet imported

## Phase 2 — Terraform (continued): Storage Account

### Resource Imported
- `azurerm_storage_account.main` → `stsecuredr01`

### Status
All core infrastructure now under Terraform management: Resource Group, 
VNet, Subnet, NSG + rules, VM, NIC, Public IP, Storage Account. 
`terraform plan` returns "No changes" across the board.

### Still Pending (Phase 2 close-out)
- `terraform destroy` + `terraform apply` full-cycle test not yet performed 
  — this is the last unverified item in FR-001's acceptance criteria.