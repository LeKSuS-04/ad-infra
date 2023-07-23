output "vpn_public_address" {
  value = yandex_compute_instance.vpn.network_interface.0.nat_ip_address
}

output "jury_public_address" {
  value = yandex_compute_instance.jury.network_interface.0.nat_ip_address
}

output "bastion_public_address" {
  value = yandex_compute_instance.bastion.network_interface.0.nat_ip_address
}

output "vulnbox_internal_addresses" {
  value = join(" ", yandex_compute_instance.vulnbox[*].network_interface.0.ip_address)
}

output "container_registry_public_address" {
  value = yandex_compute_instance.container-registry.network_interface.0.nat_ip_address
}


output "container_registry_internal_address" {
  value = yandex_compute_instance.container-registry.network_interface.0.ip_address
}
