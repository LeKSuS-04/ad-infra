resource "yandex_vpc_network" "ad_network" {
  name        = "ad-network"
  description = "main network that contains everything"
}

resource "yandex_vpc_subnet" "admin_subnet" {
  name           = "admin-subnet"
  description    = "subnet for game administrating services"
  zone           = var.yandex_cloud_zone
  network_id     = yandex_vpc_network.ad_network.id
  v4_cidr_blocks = ["192.168.1.0/24"]
}

resource "yandex_vpc_gateway" "vulnbox_nat_gateway" {
  name        = "vulnbox-nat-gateway"
  description = "NAT gateway allows vunlboxes to access internet without assigning public addresses to them"
  shared_egress_gateway {}
}

resource "yandex_vpc_route_table" "vulnbox_route_table" {
  name        = "vulnbox-route-table"
  description = "Allows to route vulnbox outcoming traffic through the NAT gateway"
  network_id  = yandex_vpc_network.ad_network.id

  static_route {
    destination_prefix = "0.0.0.0/0"
    gateway_id         = yandex_vpc_gateway.vulnbox_nat_gateway.id
  }
}

resource "yandex_vpc_subnet" "vulnbox_subnet" {
  name           = "vulnbox-subnet"
  description    = "subnet for participants' vulnboxes"
  zone           = var.yandex_cloud_zone
  network_id     = yandex_vpc_network.ad_network.id
  route_table_id = yandex_vpc_route_table.vulnbox_route_table.id
  v4_cidr_blocks = ["192.168.2.0/24"]
}