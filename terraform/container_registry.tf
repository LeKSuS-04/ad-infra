resource "yandex_vpc_address" "container_registry_ip_address" {
  name = "container-registry-address"
  external_ipv4_address {
    zone_id = var.yandex_cloud.zone
  }
}

resource "cloudflare_dns_record" "container_registry_record" {
  zone_id = var.cloudflare.zone_id
  name    = var.container_registry_vm.subdomain
  type    = "A"
  proxied = true
  content = yandex_vpc_address.container_registry_ip_address.external_ipv4_address[0].address
  ttl     = 300
}

resource "yandex_compute_instance" "container-registry" {
  description = "DockerHub mirror that caches docker images"
  name        = "container-registry"
  hostname    = "container-registry"

  resources {
    cores  = var.container_registry_vm.cores
    memory = var.container_registry_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = yandex_compute_image.ubuntu-2204-lts.id
      type     = var.container_registry_vm.disk_type
      size     = var.container_registry_vm.disk_size_gb
    }
  }

  network_interface {
    nat            = true
    nat_ip_address = yandex_vpc_address.container_registry_ip_address.external_ipv4_address[0].address

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
