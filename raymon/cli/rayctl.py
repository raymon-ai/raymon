import click
from raymon.cli.orchestration import orchestration
from raymon.cli.project import project
from raymon.cli.ray import ray
from raymon.cli.peephole import peephole


@click.group()
def cli():
    pass


cli.add_command(orchestration)
cli.add_command(project)
cli.add_command(ray)
cli.add_command(peephole)


if __name__ == '__main__':
    cli()
