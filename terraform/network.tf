locals {
  cloudflare_ip_ranges = [
    # https://www.cloudflare.com/ips-v4/#
    "173.245.48.0/20",
    "103.21.244.0/22",
    "103.22.200.0/22",
    "103.31.4.0/22",
    "141.101.64.0/18",
    "108.162.192.0/18",
    "190.93.240.0/20",
    "188.114.96.0/20",
    "197.234.240.0/22",
    "198.41.128.0/17",
    "162.158.0.0/15",
    "104.16.0.0/13",
    "104.24.0.0/14",
    "172.64.0.0/13",
    "131.0.72.0/22",
  ]
}

data "cloudflare_zone" "zone" {
  zone_id = var.cloudflare.zone_id
}

resource "yandex_vpc_network" "net" {
  description = "Main network that contains everything"
  name        = "ad-network"
}

resource "yandex_vpc_subnet" "admin_subnet" {
  description    = "Subnet for game administrating services"
  name           = "admin-subnet"
  zone           = var.yandex_cloud.zone
  network_id     = yandex_vpc_network.net.id
  v4_cidr_blocks = ["192.168.1.0/24"]
}

resource "yandex_vpc_subnet" "vulnbox_subnet" {
  description    = "Subnet for participants' vulnboxes"
  name           = "vulnbox-subnet"
  zone           = var.yandex_cloud.zone
  network_id     = yandex_vpc_network.net.id
  route_table_id = yandex_vpc_route_table.vulnbox_route_table.id
  v4_cidr_blocks = ["172.16.0.0/16"]
}

resource "yandex_vpc_route_table" "vulnbox_route_table" {
  description = "Allows to route vulnbox outcoming traffic through the NAT gateway (bastion)"
  name        = "vulnbox-route-table"
  network_id  = yandex_vpc_network.net.id

  static_route {
    destination_prefix = "0.0.0.0/0"
    next_hop_address   = yandex_compute_instance.bastion.network_interface.0.ip_address
  }
}

resource "yandex_vpc_security_group" "default_security_group" {
  name        = "default-security-group"
  description = "Default rules, which are applied to all instances in the network"
  network_id  = yandex_vpc_network.net.id

  ingress {
    description    = "Allow SSH traffic to all hosts"
    protocol       = "TCP"
    port           = 22
    v4_cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description    = "Allow all traffic to the outside world"
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "yandex_vpc_security_group" "cloudflare_protected_security_group" {
  description = "Rules for cloudflare protected hosts"
  name        = "cloudflare-protected-security-group"
  network_id  = yandex_vpc_network.net.id

  ingress {
    description    = "Allow HTTP traffic from cloudflare ip ranges"
    protocol       = "TCP"
    port           = 80
    v4_cidr_blocks = local.cloudflare_ip_ranges
  }
}
