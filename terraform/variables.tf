variable "my_ip_address" {
  description = "Your current public IP address, used to restrict SSH access"
  type        = string
  sensitive   = true
}