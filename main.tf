provider "yandex" {
  zone                     = var.yandex_cloud.zone
  service_account_key_file = var.yandex_cloud.service_account_key_file
  folder_id                = var.yandex_cloud.folder_id
  storage_access_key       = var.yandex_cloud.static_key.access_key
  storage_secret_key       = var.yandex_cloud.static_key.secret_key
}

locals {
  debian11_image_id = "fd8mejp64t7hgh4rfs93"

  default_metadata = {
    serial-port-enable = 0
    user-data          = file("./scripts/remote/init_instance.sh")
    admin-accounts     = jsonencode(var.admin_accounts)
  }

  default_local_environment = {
    RESULT_DIR = (
      startswith(var.local_dirs.result_dir, "/")
      ? var.local_dirs.result_dir
      : join("/", [abspath("."), var.local_dirs.result_dir])
    )
    TEMP_DIR = (
      startswith(var.local_dirs.temp_dir, "/")
      ? var.local_dirs.temp_dir
      : join("/", [abspath("."), var.local_dirs.temp_dir])
    )
    SRC_DIR = (
      startswith(var.local_dirs.src_dir, "/")
      ? var.local_dirs.src_dir
      : join("/", [abspath("."), var.local_dirs.src_dir])
    )
  }

  team_count    = length(var.teams_config.teams) + (var.teams_config.add_npc ? 1 : 0)
  service_count = length(var.forcad_config.tasks)

  forcad_full_config = {
    admin = var.forcad_config.admin,
    game = merge(var.forcad_config.game, {
      start_time = var.network_config.open_time
      timezone   = var.network_config.timezone
    })
    teams = concat(
      [
        for i, team_name in var.teams_config.teams : {
          ip   = format("10.%d.%d.2", 80 + floor((i + 1) / 256), (i + 1) % 256)
          name = team_name
        }
      ],
      (
        var.teams_config.add_npc
        ? [{
          ip = format(
            "10.%d.%d.2",
            80 + floor((length(var.teams_config.teams) + 1) / 256),
            (length(var.teams_config.teams) + 1) % 256
          )
          name = "🤖 NPC"
        }]
        : []
      )
    ),
    tasks = var.forcad_config.tasks
  }
}

resource "null_resource" "prepare_local" {
  # Prepare local machine for execution of scripts
  provisioner "local-exec" {
    command     = "./scripts/local/prepare_apply.sh"
    environment = merge(local.default_local_environment, {})
  }
}

resource "yandex_vpc_network" "main_network" {
  description = "Global network for instances"
  name        = "main_network"
}

resource "yandex_vpc_subnet" "main_subnet" {
  description    = "Subnet for vpn and jury servers"
  name           = "main_subnet"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.main_network.id
  v4_cidr_blocks = ["192.168.1.0/24"]
}

resource "yandex_compute_instance" "vpn_server" {
  # Server that sets up VPN configs and acts as VPN server afterwards
  description = "VPN server"
  name        = "vpn-server"
  hostname    = "vpn-server"
  depends_on  = [null_resource.prepare_local]

  resources {
    cores         = 2
    core_fraction = 100
    memory        = 2
  }

  boot_disk {
    auto_delete = true
    device_name = "vpn"
    initialize_params {
      size     = 10
      type     = "network-ssd"
      image_id = local.debian11_image_id
    }
  }

  network_interface {
    nat       = true
    ipv4      = true
    subnet_id = yandex_vpc_subnet.main_subnet.id
  }

  metadata = merge(local.default_metadata, {
    teams-config = jsonencode({
      team_count       = local.team_count,
      players_per_team = var.teams_config.players_per_team,
    }),
    network-config = jsonencode(var.network_config)
  })

  connection {
    type        = "ssh"
    user        = var.admin_private_key.username
    host        = self.network_interface.0.nat_ip_address
    private_key = file(var.admin_private_key.private_ssh_key_location)
  }

  provisioner "file" {
    source      = join("/", [local.default_local_environment.TEMP_DIR, "services.zip"])
    destination = join("/", ["/home", var.admin_private_key.username, "services.zip"])
  }

  provisioner "remote-exec" {
    script = "./scripts/remote/vpn_server.sh"
  }

  provisioner "local-exec" {
    command = "./scripts/local/vpn_fetch_configs.sh"
    environment = merge(local.default_local_environment, {
      HOST             = self.network_interface.0.nat_ip_address
      USER             = var.admin_private_key.username
      PRIVATE_KEY_PATH = var.admin_private_key.private_ssh_key_location
    })
  }
}

resource "yandex_compute_instance" "jury_server" {
  description = "Jury server"
  name        = "juryserver"
  hostname    = "juryserver"

  # Because jury server requires VPN client configs to be generated
  depends_on = [yandex_compute_instance.vpn_server]

  resources {
    cores         = 2
    core_fraction = 100
    memory        = 4
  }

  boot_disk {
    auto_delete = true
    initialize_params {
      size     = 20
      type     = "network-ssd"
      image_id = local.debian11_image_id
    }
  }

  network_interface {
    nat       = true
    ipv4      = true
    subnet_id = yandex_vpc_subnet.main_subnet.id
  }

  metadata = merge(local.default_metadata, {
    forcad-config = jsonencode(local.forcad_full_config)
  })

  connection {
    type        = "ssh"
    user        = var.admin_private_key.username
    host        = self.network_interface.0.nat_ip_address
    private_key = file(var.admin_private_key.private_ssh_key_location)
  }

  provisioner "file" {
    source      = join("/", [local.default_local_environment.TEMP_DIR, "jury", "config.ovpn"])
    destination = join("/", ["/home", var.admin_private_key.username, "config.ovpn"])
  }

  provisioner "file" {
    source      = join("/", [local.default_local_environment.TEMP_DIR, "checkers.zip"])
    destination = join("/", ["/home", var.admin_private_key.username, "checkers.zip"])
  }

  provisioner "remote-exec" {
    script = "./scripts/remote/jury_server.sh"
  }

  provisioner "local-exec" {
    command = "./scripts/local/jury_fetch_tokens.sh"
    environment = merge(local.default_local_environment, {
      HOST             = self.network_interface.0.nat_ip_address
      USER             = var.admin_private_key.username
      PRIVATE_KEY_PATH = var.admin_private_key.private_ssh_key_location
    })
  }
}

resource "yandex_vpc_gateway" "nat_gateway" {
  name = "test-gateway"
  shared_egress_gateway {}
}

resource "yandex_vpc_route_table" "vulnbox_route_table" {
  description = "NAT route table"
  name        = "vulnbox-route-table"
  network_id  = yandex_vpc_network.main_network.id

  static_route {
    destination_prefix = "0.0.0.0/0"
    gateway_id         = yandex_vpc_gateway.nat_gateway.id
  }
}

resource "yandex_vpc_subnet" "vulnbox_subnet" {
  description    = "Subnet for vulnboxes"
  name           = "vulnbox_subnet"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.main_network.id
  route_table_id = yandex_vpc_route_table.vulnbox_route_table.id
  v4_cidr_blocks = ["192.168.10.0/24"]
}

resource "random_string" "team_password" {
  # Unique password for each vulnbox
  count   = local.team_count
  length  = 16
  special = false
  upper   = true
  lower   = true
  numeric = true
}

resource "yandex_storage_bucket" "services_bucket" {
  # Bucket for archive with services
  bucket_prefix = "services-"

  max_size              = 0
  default_storage_class = "STANDARD"
  force_destroy         = true
  anonymous_access_flags {
    read = true
    list = false
  }
}

resource "random_string" "vulnbox_vpn_client_postfix" {
  # Identificator of vunlbox VPN config in bucket. Unique for each team
  count   = local.team_count
  length  = 16
  special = false
  upper   = true
  lower   = true
  numeric = true
}

resource "yandex_storage_object" "vulnbox_vpn_client" {
  # Unique VPN client for each vulnbox
  count = local.team_count

  depends_on = [
    null_resource.prepare_local,
    yandex_compute_instance.vpn_server
  ]

  bucket = yandex_storage_bucket.services_bucket.bucket
  key    = format("vunlbox%03d-%s.ovpn", count.index + 1, random_string.vulnbox_vpn_client_postfix[count.index].result)
  source = join("/", [local.default_local_environment.TEMP_DIR, "vuln", format("vuln%03d.ovpn", count.index + 1)])
}

resource "yandex_storage_object" "services" {
  # Services archive stored in bucket

  # Because services need to be packed
  depends_on = [null_resource.prepare_local]

  bucket = yandex_storage_bucket.services_bucket.bucket
  key    = "services.zip"
  source = join("/", [local.default_local_environment.TEMP_DIR, "services.zip"])
}

resource "yandex_compute_instance" "vulnbox" {
  # Vulnboxes themselves
  description = "Vulbox for team ${count.index + 1}"
  count       = local.team_count
  name        = format("vulnbox%03d", count.index + 1)
  hostname    = format("vulnbox%03d", count.index + 1)

  resources {
    cores         = 2 * ceil(local.service_count / 4)
    core_fraction = 100
    memory        = 2 * ceil(local.service_count / 4)
  }

  boot_disk {
    auto_delete = true
    initialize_params {
      size     = 5 + 2 * local.service_count
      type     = "network-ssd"
      image_id = local.debian11_image_id
    }
  }

  network_interface {
    ipv4      = true
    subnet_id = yandex_vpc_subnet.vulnbox_subnet.id
  }

  metadata = merge(local.default_metadata, {
    team-number = count.index + 1
    password    = random_string.team_password[count.index].result

    user-data = join("\n", [
      file("./scripts/remote/init_instance.sh"),
      "sudo -u ${var.admin_private_key.username} bash << 'END'",
      file("./scripts/remote/vuln_server.sh"),
      "END",
      ""
    ])

    bucket                = yandex_storage_bucket.services_bucket.bucket
    services-resource-key = yandex_storage_object.services.key
    vpn-config-key        = yandex_storage_object.vulnbox_vpn_client[count.index].id
  })

  provisioner "local-exec" {
    command = "./scripts/local/vulnbox_write_password.sh"
    environment = merge(local.default_local_environment, {
      TEAM_NUMBER = format("%03d", count.index + 1)
      PASSWORD    = random_string.team_password[count.index].result
    })
  }
}

resource "null_resource" "pack_team_archives" {
  # This script requires all data from vpn, jury and vulnboxes.
  # More precisely, it needs:
  # * Team VPN clients from vpn server
  # * Team tokens from jury server
  # * User passwords from team vulnbox
  depends_on = [
    yandex_compute_instance.vpn_server,
    yandex_compute_instance.jury_server,
    yandex_compute_instance.vulnbox
  ]

  provisioner "local-exec" {
    command = "./scripts/local/pack_team_archives.sh"
    environment = merge(local.default_local_environment, {
      TEAMS_CONFIG_JSON   = jsonencode(var.teams_config)
      NETWORK_CONFIG_JSON = jsonencode(var.network_config)
      FORCAD_CONFIG_JSON  = jsonencode(var.forcad_config)
      JURY_PUBLIC_IP      = yandex_compute_instance.jury_server.network_interface.0.nat_ip_address
    })
  }
}

resource "null_resource" "cleanup" {
  # Cleans local system after mish-mash with creating team archives

  # Because this needs to be executed only after everything else was finished
  depends_on = [null_resource.pack_team_archives]

  provisioner "local-exec" {
    command     = "./scripts/local/cleanup.sh"
    environment = merge(local.default_local_environment, {})
  }
}
