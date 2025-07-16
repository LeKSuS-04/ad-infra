output "addresses" {
  value = {
    "protected" : {
      "jury" : "${var.jury_vm.subdomain}.${data.cloudflare_zone.zone.name}",
      "monitoring" : "${var.monitoring_vm.subdomain}.${data.cloudflare_zone.zone.name}",
    },
    "open" : {
      "vpn" : {
        "raw" : yandex_vpc_address.vpn_ip_address.external_ipv4_address[0].address,
        "dns" : "${var.vpn_vm.subdomain}.${data.cloudflare_zone.zone.name}",
      },
      "bastion" : {
        "raw" : yandex_vpc_address.bastion_ip_address.external_ipv4_address[0].address,
        "dns" : "${var.bastion_vm.subdomain}.${data.cloudflare_zone.zone.name}",
      },
      "jury" : {
        "raw" : yandex_vpc_address.jury_ip_address.external_ipv4_address[0].address,
      },
      "container_registry" : {
        "raw" : yandex_vpc_address.container_registry_ip_address.external_ipv4_address[0].address,
        "dns" : "${var.container_registry_vm.subdomain}.${data.cloudflare_zone.zone.name}",
      },
      "monitoring" : {
        "raw" : yandex_vpc_address.monitoring_ip_address.external_ipv4_address[0].address,
      },
    },
    "internal" : {
      "vulnboxes" : [for i, instance in zipmap(var.vulnbox_numbers, yandex_compute_instance.vulnbox) : {
        "number" : i,
        "ip" : instance.network_interface.0.ip_address
      }]
    }
  }
}
