import click

import handlers


@click.group()
def cli():
    pass


@cli.command('deploy')
def deploy():
    ''' Deploy everything '''
    handlers.deploy()
