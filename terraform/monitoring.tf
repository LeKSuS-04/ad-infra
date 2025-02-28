resource "yandex_vpc_address" "monitoring_ip_address" {
  name = "monitoring-address"
  external_ipv4_address {
    zone_id = var.yandex_cloud.zone
  }
}

resource "cloudflare_dns_record" "monitoring_record" {
  zone_id = var.cloudflare.zone_id
  name    = var.monitoring_vm.subdomain
  type    = "A"
  proxied = true
  content = yandex_vpc_address.monitoring_ip_address.external_ipv4_address[0].address
  ttl     = 1
}

resource "yandex_compute_instance" "monitoring" {
  description = "Monitoring server"
  name        = "monitoring"
  hostname    = "monitoring"

  resources {
    cores  = var.monitoring_vm.cores
    memory = var.monitoring_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = yandex_compute_image.ubuntu-2404-lts.id
      type     = var.monitoring_vm.disk_type
      size     = var.monitoring_vm.disk_size_gb
    }
  }

  network_interface {
    nat            = true
    nat_ip_address = yandex_vpc_address.monitoring_ip_address.external_ipv4_address[0].address

    subnet_id = yandex_vpc_subnet.admin_subnet.id
    # security_group_ids = [
    #   yandex_vpc_security_group.default_security_group.id
    # ]
  }

  metadata = {
    serial-port-enable = 1
    user-data          = local.cloud_init_config
  }
}
