variable "yandex_cloud" {
  description = "Configuration of yandex cloud provider"
  type = object({
    folder_id = string
    iam_token = string
    zone      = string
  })
  nullable = false
}

variable "vulnbox_count" {
  description = "Amount of vulnboxes to create"
  type        = number
  nullable    = false
}

variable "jury_vm" {
  description = "Resources of jury vm"
  type = object({
    cores  = number
    ram_gb = number
    ssd_gb = number
  })
  nullable = false
}

variable "vpn_vm" {
  description = "Resources of VPN vm"
  type = object({
    cores  = number
    ram_gb = number
    ssd_gb = number
  })
  nullable = false
}

variable "vulnbox_vm" {
  description = "Resources of vulnbox vm"
  type = object({
    cores  = number
    ram_gb = number
    ssd_gb = number
  })
  nullable = false
}

variable "bastion_vm" {
  description = "Resources of bastion vm"
  type = object({
    cores  = number
    ram_gb = number
    ssd_gb = number
  })
  nullable = false
}

variable "container_registry_vm" {
  description = "Resources of container registry vm"
  type = object({
    cores  = number
    ram_gb = number
    ssd_gb = number
  })
  nullable = false
}
