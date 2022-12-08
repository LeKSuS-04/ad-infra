output "jury_server_ip" {
  description = "External ip address of jury server"
  value = yandex_compute_instance.jury_server.network_interface.0.nat_ip_address
}
