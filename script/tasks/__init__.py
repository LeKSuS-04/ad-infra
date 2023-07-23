from . import ansible, other, terraform, vpn

TASK_LIST = [
    other.clean_filesystem,
    other.get_ssh_keys,
    other.load_config,
    other.map_teams_to_vulnbox_configs,
    other.pack_team_archives,
    other.save_forcad_config,
    other.plan_resources,
    other.prepare_docker_config,
    #
    ansible.start_forcad,
    ansible.configure_jury,
    ansible.configure_vpn,
    ansible.configure_vulnboxes,
    ansible.configure_container_registry,
    ansible.ping_all_hosts,
    ansible.prepare_ansible,
    #
    terraform.deploy_infrastructure,
    terraform.destroy_infrastructure,
    terraform.save_terraform_config,
    #
    vpn.create_configs,
]
