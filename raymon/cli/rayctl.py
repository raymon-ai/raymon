import click
from raymon.cli.orchestration import orchestration
from raymon.cli.project import project
from raymon.cli.ray import ray
from raymon.cli.peephole import peephole
from raymon.cli.piperesult import piperesult
from raymon.cli.object import result


@click.group()
def cli():
    pass


cli.add_command(orchestration)
cli.add_command(project)
cli.add_command(ray)
# cli.add_command(peephole)
# cli.add_command(piperesult)
cli.add_command(result)


if __name__ == "__main__":
    cli()
