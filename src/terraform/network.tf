resource "yandex_vpc_network" "ad_network" {
  description = "Main network that contains everything"
  name        = "ad-network"
}

resource "yandex_vpc_subnet" "admin_subnet" {
  description    = "Subnet for game administrating services"
  name           = "admin-subnet"
  zone           = var.yandex_cloud.zone
  network_id     = yandex_vpc_network.ad_network.id
  v4_cidr_blocks = ["192.168.1.0/24"]
}

resource "yandex_vpc_subnet" "vulnbox_subnet" {
  description    = "Subnet for participants' vulnboxes"
  name           = "vulnbox-subnet"
  zone           = var.yandex_cloud.zone
  network_id     = yandex_vpc_network.ad_network.id
  route_table_id = yandex_vpc_route_table.vulnbox_route_table.id
  v4_cidr_blocks = ["192.168.2.0/24"]
}

resource "yandex_vpc_route_table" "vulnbox_route_table" {
  description = "Allows to route vulnbox outcoming traffic through the NAT gateway (bastion)"
  name        = "vulnbox-route-table"
  network_id  = yandex_vpc_network.ad_network.id

  static_route {
    destination_prefix = "0.0.0.0/0"
    next_hop_address   = yandex_compute_instance.bastion.network_interface.0.ip_address
  }
}
