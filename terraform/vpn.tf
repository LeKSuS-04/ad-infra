locals {
  vpn_static_ip = "192.168.1.11"
}

resource "yandex_vpc_address" "vpn_ip_address" {
  name = "vpn-address"
  external_ipv4_address {
    zone_id = var.yandex_cloud.zone
  }
}

resource "cloudflare_dns_record" "vpn_record" {
  zone_id = var.cloudflare.zone_id
  name    = var.vpn_vm.subdomain
  type    = "A"
  proxied = true
  content = yandex_vpc_address.vpn_ip_address.external_ipv4_address[0].address
  ttl     = 300
}

# resource "yandex_vpc_security_group" "cloudflare_protected_security_group" {
#   description = "Rules for cloudflare protected hosts"
#   name        = "cloudflare-protected-security-group"
#   network_id  = yandex_vpc_network.net.id

#   ingress {
#     description    = "Allow wireguard traffic"
#     protocol       = "UDP"
#     port           = var.vpn_vm.wireguard_port
#     v4_cidr_blocks = ["0.0.0.0/0"]
#   }
# }

resource "yandex_compute_instance" "vpn" {
  description = "Host for game VPN network"
  name        = "vpn"
  hostname    = "vpn"

  resources {
    cores  = var.vpn_vm.cores
    memory = var.vpn_vm.ram_gb
  }

  boot_disk {
    initialize_params {
      image_id = yandex_compute_image.ubuntu-2204-lts.id
      type     = var.vpn_vm.disk_type
      size     = var.vpn_vm.disk_size_gb
    }
  }

  network_interface {
    nat            = true
    nat_ip_address = yandex_vpc_address.vpn_ip_address.external_ipv4_address[0].address

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
