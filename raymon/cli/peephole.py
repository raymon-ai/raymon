import json
import click
import yaml
import requests
import msgpack
from raymon.loggers import RaymonAPI


@click.group()
def peephole():
    pass


@click.command()
@click.option("--project-id", help="The name of the project you want to list the rays for")
def ls(project_id):
    api = RaymonAPI(url="http://localhost:8000")
    api.login()
    params = {"project_id": project_id}
    resp = api.get(route=f"peephole", params=params).json()
    click.echo(f"{'Ray id':40s} - {'peephole':20s} - {'ts':20s}")

    for peep in resp["peepholes"]:
        click.echo(f"{peep['ray_id']:40s} - {peep['peephole']:20s} - {peep['ts']:20s}")


peephole.add_command(ls)

if __name__ == "__main__":
    peephole()
