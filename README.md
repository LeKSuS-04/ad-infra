# AD-INFRA

Dockerized tool for deploying attack-defense CTFs to Yandex cloud

### Lifecycle

1. Process configs and generate config for "archiver"
2. Archive services and checkers

3. Generate config for deployment and configuration of VPN server
4. Deploy VPN server, get server IP
5. Generate VPN configs using OVPNGen
5. Configure VPN server:
    * Get VPN configs there
    * Initialise network controller
    * Set up timers to open and close network at required times

6. 

### Configuration

`/src` must contain configuration variables for your deployment.

* [Required variables](/src/variables.tf)
* [Variable definitions files in Terraform](https://developer.hashicorp.com/terraform/language/values/variables#variable-definitions-tfvars-files)
