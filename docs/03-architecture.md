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