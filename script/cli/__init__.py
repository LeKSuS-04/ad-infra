import click
from tasks import ansible, other, terraform

from .utils import run_tasks_with_manager


@click.group()
def cli():
    pass


@cli.command("deploy")
def deploy():
    """Deploy everything."""
    run_tasks_with_manager(
        ansible.configure_vpn,
        ansible.configure_jury,
        ansible.configure_vulnboxes,
        other.pack_team_archives,
    )


@cli.command("destroy")
def destroy():
    """Destroy everything and clean up filesystem."""
    run_tasks_with_manager(
        terraform.destroy_infrastructure,
        other.clean_filesystem,
    )


@cli.command("plan")
def plan():
    """Calculate resource usage."""
    run_tasks_with_manager(other.plan_resources)
