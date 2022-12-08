variable "yandex_cloud" {
  description = "Yandex cloud configuration"
  type = object({
    folder_id                = string
    zone                     = string
    service_account_key_file = string
    static_key = object({
      access_key = string
      secret_key = string
    })
  })
}

variable "admin_accounts" {
  description = "List of administrator accounts to add to hosts. Must contain at least one entry"
  type = list(object({
    username       = string
    public_ssh_key = string
  }))

  validation {
    condition     = length(var.admin_accounts) > 0
    error_message = "List of admin accounts must contain at least one entry"
  }
}

variable "admin_private_key" {
  description = "Private key required to allow automated access to infrastructure after it is generated"
  type = object({
    username                 = string
    private_ssh_key_location = string
  })

  validation {
    condition     = fileexists(var.admin_private_key.private_ssh_key_location)
    error_message = "admin private key doesn't exist at specified location"
  }
}

variable "network_config" {
  description = "Configuration of VPN network"
  type = object({
    open_time  = string
    close_time = string
    timezone   = string
  })
}

variable "forcad_config" {
  description = "Configuration of ForcAD platform"
  type = object({
    admin = object({
      username = string
      password = string
    })

    game = object({
      mode       = string
      round_time = number

      default_score = number
      flag_lifetime = number
      game_hardness = number
      inflation     = bool
    })

    tasks = list(object({
      checker         = string
      checker_timeout = number
      checker_type    = string
      gets            = number
      name            = string
      places          = number
      puts            = number
    }))
  })
}

variable "teams_config" {
  description = "Configuration of teams that participate in competition"
  type = object({
    add_npc          = bool
    players_per_team = number
    teams            = list(string)
  })

  validation {
    condition     = var.teams_config.players_per_team > 0
    error_message = "You need at least 1 player per team, silly!"
  }

  validation {
    condition     = length(var.teams_config.teams) > 0
    error_message = "You need at least 1 team to play, silly!"
  }
}

variable "local_dirs" {
  description = "Configuration of local directories, used in script"
  type = object({
    temp_dir   = string
    result_dir = string
    src_dir    = string
  })
}
