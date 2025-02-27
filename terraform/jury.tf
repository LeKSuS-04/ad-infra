resource "yandex_vpc_address" "jury_ip_address" {
  name = "jury-address"
  external_ipv4_address {
    zone_id = var.yandex_cloud.zone
  }
}

resource "cloudflare_dns_record" "ctfd_record" {
  zone_id = var.cloudflare.zone_id
  name    = var.jury_vm.subdomain
  type    = "A"
  proxied = true
  content = yandex_vpc_address.jury_ip_address.external_ipv4_address[0].address
  ttl     = 300
}

resource "yandex_compute_instance" "jury" {
  description = "Jury server that contains checksystem"
  name        = "jury"
  hostname    = "jury"

  resources {
    cores  = var.jury_vm.cores
    memory = var.jury_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = yandex_compute_image.ubuntu-2204-lts.id
      type     = var.jury_vm.disk_type
      size     = var.jury_vm.disk_size_gb
    }
  }

  network_interface {
    nat            = true
    nat_ip_address = yandex_vpc_address.jury_ip_address.external_ipv4_address[0].address

    subnet_id = yandex_vpc_subnet.admin_subnet.id
    # security_group_ids = [
    # yandex_vpc_security_group.cloudflare_protected_security_group.id,
    # yandex_vpc_security_group.default_security_group.id
    # ]
  }

  metadata = {
    serial-port-enable = 1
    user-data          = local.cloud_init_config
  }
}
