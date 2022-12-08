# Deploy-AD

Terraform script to deploy your Attack-Defense CTF to the cloud

## Installation

Just clone the repo

```bash
git clone <...>
```

## Configuration

Example configuration can be found in `terraform.tfvars.example`. Copy and
modify it before the deployment:

```bash
cp terraform.tfvars.example terraform.tfvars
```

### Configuration file reference

- `yandex_cloud`: Cloud configuration
  - `folder_id`: [Folder](https://cloud.yandex.com/en-ru/docs/resource-manager/operations/#folder) that will contain infrastructure
  - `zone`: [Availability zone](https://cloud.yandex.com/en-ru/docs/overview/concepts/geo-scope), in which infrastructure will be placed
  - `serice_account_key_file`: [Key file for service account](https://cloud.yandex.com/en-ru/docs/cli/operations/authentication/service-account#auth-as-sa)
  - `static_key`: [Static key](https://cloud.yandex.com/en-ru/docs/iam/concepts/authorization/access-key) to access bucket storages
    - `access_key`: [Access part](https://cloud.yandex.com/en-ru/docs/iam/concepts/authorization/access-key) of static key
    - `secret_key`: [Secret part](https://cloud.yandex.com/en-ru/docs/iam/concepts/authorization/access-key) of static key
- `admin_accounts`: List of administrator accounts, which will be placed at every
  cloud instance and granted sudo priveleges.
  - `username`: Username of administrator account
  - `public_ssh_key`: Public ssh key of account to provide ssh access to the instance
- `admin_private_key`: Private key of one of the administrators. Administrator
  account with this key is used to set up all instances via ssh, so this must exist.
  - `username`: Username of administrator account
  - `private_ssh_key_location`: Path to the private ssh key on the local machine
- `network_config`: Configuration of VPN network. Time must be in format `YYYY-MM-DD hh:mm:ss`
  - `open_time`: Time to open network and launch checkers
  - `close_time`: Time to close network
  - `timezone`: Specify timezone
- `forcad_config`: Configuration of ForcAD. Parameters that must be specified in could be found in [variables.tf](./variables.tf)
- `teams_config`: Configuration of teams
  - `add_npc`: Whether to add NPC player or not
  - `players_per_team`: How many VPN configs per team should be generated
  - `teams`: list of strings with team names
- `local_dirs`: Directories, used by local scripts. Will be created, if not exist
  - `result_dir`: VPN configs for teams will be saved here
  - `temp_dir`: Directory for temporary file placement, will be cleaned after execution
  - `src_dir`: Directory which contains services and checkers. Must be structured exactly as described [here](https://github.com/pomo-mondreganto/ad-boilerplate/tree/master)

### Example

[LeKSuS-04/ad-training-03-11-2022](https://github.com/LeKSuS-04/ad-training-03-11-2022/tree/master)
is used as an example of service repository. All example configurations are compatible with it.
