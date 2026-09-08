variable "my_ip_addresses" {
  description = "List of trusted public IPs allowed to SSH in"
  type        = list(string)
  sensitive   = true
}