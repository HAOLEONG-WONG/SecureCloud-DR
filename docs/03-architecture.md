# Architecture — Phase 1 Progress

## Resources Created So Far
- Resource Group: `rg-securecloud-dr-lab`
- Virtual Network: `vnet-securecloud-dr` (10.0.0.0/16), region: Malaysia West
- Subnet: `snet-web` (10.0.0.0/24)
- Network Security Group: `nsg-web` — inbound rule allows SSH (port 22) only from my current IP

## Notes
- Region constrained to Azure for Students allowed list: uaenorth, eastasia, malaysiawest, indiasouthcentral, indonesiacentral
- Chose Malaysia West for lowest latency