import click

from raymon.cli.orchestration import orchestration


@click.group()
def cli():
    pass


cli.add_command(orchestration)

if __name__ == '__main__':
    cli()
