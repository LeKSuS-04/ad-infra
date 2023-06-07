import click

import handlers


@click.group()
def cli():
    pass


@cli.command("deploy")
def deploy():
    """Deploy everything"""
    handlers.deploy()


@cli.command("destroy")
def destroy():
    """Destroy everything and clean up filesystem"""
    handlers.destroy()
