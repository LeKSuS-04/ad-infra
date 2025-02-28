output "addresses" {
  value = {
    "protected" : {
      "jury" : "${var.jury_vm.subdomain}.${data.cloudflare_zone.zone.name}",
      "monitoring" : "${var.monitoring_vm.subdomain}.${data.cloudflare_zone.zone.name}",
    },
    "open" : {
      "vpn" : "${var.vpn_vm.subdomain}.${data.cloudflare_zone.zone.name}",
      "bastion" : "${var.bastion_vm.subdomain}.${data.cloudflare_zone.zone.name}",
      "jury" : yandex_vpc_address.jury_ip_address.external_ipv4_address[0].address,
      "container_registry" : "${var.container_registry_vm.subdomain}.${data.cloudflare_zone.zone.name}",
      "monitoring" : yandex_vpc_address.monitoring_ip_address.external_ipv4_address[0].address,
    },
    "internal" : {
      "vulnboxes" : [for instance in yandex_compute_instance.vulnbox : instance.network_interface.0.ip_address]
    }
  }
}
