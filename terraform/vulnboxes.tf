resource "yandex_compute_image" "nat-instance-ubuntu" {
  description   = "NAT image based on Ubuntu 22.04 LTS with predefined routing and ip forwarding rules"
  name          = "nat-instance-ubuntu-2204"
  source_family = "nat-instance-ubuntu-2204"
}

resource "yandex_vpc_address" "bastion_ip_address" {
  name = "bastion-address"
  external_ipv4_address {
    zone_id = var.yandex_cloud.zone
  }
}

resource "cloudflare_dns_record" "bastion_record" {
  zone_id = var.cloudflare.zone_id
  name    = var.bastion_vm.subdomain
  type    = "A"
  proxied = false
  content = yandex_vpc_address.bastion_ip_address.external_ipv4_address[0].address
  ttl     = 1
}

resource "yandex_compute_instance" "bastion" {
  description = "SSH bastion that provides access to vulnbox instances. Also acts as a NAT gateway"
  name        = "bastion"
  hostname    = "bastion"

  resources {
    cores  = var.bastion_vm.cores
    memory = var.bastion_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = yandex_compute_image.nat-instance-ubuntu.id
      type     = var.bastion_vm.disk_type
      size     = var.bastion_vm.disk_size_gb
    }
  }

  network_interface {
    nat            = true
    nat_ip_address = yandex_vpc_address.bastion_ip_address.external_ipv4_address[0].address

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

resource "yandex_compute_instance" "vulnbox" {
  description = "Vulnbox for team ${var.vulnbox_numbers[count.index]}"
  count       = length(var.vulnbox_numbers)
  name        = format("vulnbox%03d", var.vulnbox_numbers[count.index])
  hostname    = format("vulnbox%03d", var.vulnbox_numbers[count.index])

  resources {
    cores  = var.vulnbox_vm.cores
    memory = var.vulnbox_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = yandex_compute_image.ubuntu-2404-lts.id
      type     = var.vulnbox_vm.disk_type
      size     = var.vulnbox_vm.disk_size_gb
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.vulnbox_subnet.id
    nat       = false
  }

  metadata = {
    serial-port-enable = 1
    user-data          = local.cloud_init_config
  }
}
