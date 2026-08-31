   ## Known Limitation
   IAM/RBAC multi-identity testing deferred due to personal Microsoft account 
   authentication issue (tenant token conflict). Will revisit with fresh account 
   or alternative approach (Service Principal / App Registration) in later session.

   # Security Design — Phase 1

## Network Security

### NSG Rules (`nsg-web`)
| Rule | Purpose |
|---|---|
| Allow-SSH-MyIP (port 22, source = my current IP) | Restricts SSH access to a single known IP instead of the internet at large, reducing attack surface for brute-force attempts |

**Design decision:** VM's "Public inbound ports" was set to None during creation, relying entirely on the custom NSG instead of Azure's default port rules — this avoids having two separate, potentially conflicting network security layers.

**Known limitation:** the allowed source IP is my current dynamic ISP-assigned IP. If SSH access fails in a future session, the likely cause is IP change — the NSG rule will need updating.

## Identity & Access Management (IAM)

**Planned design (per project spec §12):** four distinct identities — Administrator, Security Analyst, Application Identity, Test Attacker — each with different RBAC privilege levels, to demonstrate least-privilege access control.

**Known Limitation:** Multi-identity RBAC testing was deferred. Azure for Students subscriptions are bound to the institution's Entra ID tenant, where student accounts lack User Administrator / Global Administrator rights needed to create new users. Attempted workaround (creating a separate personal Entra ID tenant) hit an unresolved authentication/session bug specific to the personal Microsoft account used.

**Next steps considered:**
- Retry with a freshly registered Microsoft account (isolate from any prior account conflicts)
- Alternative: use Service Principals / App Registrations instead of user accounts to demonstrate least-privilege concepts, since these don't require the same tenant-level user-creation permissions

## Storage Account Security (`stsecuredr01`)
- Blob anonymous access: Disabled
- Secure transfer (HTTPS only): Enabled
- Minimum TLS version: 1.2
- **Known tradeoff:** Storage account key access remains enabled rather than enforcing Entra ID-only authentication — acceptable for this lab stage, but noted as a design compromise that would be tightened in a production environment.

## Region Constraint
Subscription policy restricts deployable regions to: `uaenorth`, `eastasia`, `malaysiawest`, `indiasouthcentral`, `indonesiacentral`. Selected `malaysiawest` for lowest latency given project location.