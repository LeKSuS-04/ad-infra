variable "yandex_cloud" {
  description = "Configuration of yandex cloud provider"
  type = object({
    folder_id = string
    zone      = string
  })
  nullable = false
}

variable "cloudflare" {
  description = "Configuration of cloudflare provider"
  type = object({
    zone_id = string
  })
  nullable = false
}

variable "vulnbox_count" {
  description = "Amount of vulnboxes to create"
  type        = number
  nullable    = false
}

variable "jury_vm" {
  description = "Configuration of jury vm"
  type = object({
    subdomain    = string
    cores        = number
    ram_gb       = number
    disk_type    = string
    disk_size_gb = number
  })
  nullable = false
}

variable "vpn_vm" {
  description = "Configuration of VPN vm"
  type = object({
    subdomain      = string
    cores          = number
    ram_gb         = number
    disk_type      = string
    disk_size_gb   = number
    wireguard_port = number
  })
  nullable = false
}

variable "vulnbox_vm" {
  description = "Configuration of vulnbox vm"
  type = object({
    cores        = number
    ram_gb       = number
    disk_type    = string
    disk_size_gb = number
  })
  nullable = false
}

variable "bastion_vm" {
  description = "Configuration of bastion vm"
  type = object({
    subdomain    = string
    cores        = number
    ram_gb       = number
    disk_type    = string
    disk_size_gb = number
  })
  nullable = false
}

variable "container_registry_vm" {
  description = "Configuration of container registry vm"
  type = object({
    subdomain    = string
    cores        = number
    ram_gb       = number
    disk_type    = string
    disk_size_gb = number
  })
  nullable = false
}

variable "monitoring_vm" {
  description = "Configuration of monitoring vm"
  type = object({
    subdomain    = string
    cores        = number
    ram_gb       = number
    disk_type    = string
    disk_size_gb = number
  })
  nullable = false
}

variable "admin_user" {
  description = "Configuration of admin user"
  type = object({
    username = string
    password = optional(string)
    ssh_keys = list(string)
  })
  nullable = false
}
