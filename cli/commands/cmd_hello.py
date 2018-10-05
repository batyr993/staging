import subprocess

import click


@click.command()
@click.argument('name', default='batyr')
def cli(name):
	cmd = 'Hello {0}'.format(name)
	click.echo(cmd)
	