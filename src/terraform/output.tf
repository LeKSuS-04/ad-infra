output "vpn_address" {
  value = yandex_compute_instance.vpn.network_interface.0.nat_ip_address
}

output "jury_address" {
  value = yandex_compute_instance.jury.network_interface.0.nat_ip_address
}

output "bastion_address" {
  value = yandex_compute_instance.bastion.network_interface.0.nat_ip_address
}

output "vulnbox_internal_addresses" {
  value = join(" ", yandex_compute_instance.vulnbox[*].network_interface.0.ip_address)
}