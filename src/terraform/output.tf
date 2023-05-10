output "vpn_address" {
  value = yandex_compute_instance.vpn_server.network_interface.0.nat_ip_address
}
