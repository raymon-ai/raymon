import json
import click
import yaml
import requests
import msgpack
from raymon.loggers import RaymonAPI


@click.group()
def ref():
    pass


@click.command()
@click.option("--project-id", help="The name of the project you want to list the rays for")
def ls(project_id):
    api = RaymonAPI(url="http://localhost:8000")
    api.login()
    params = {"project_id": project_id}
    resp = api.get(route=f"ref", params=params).json()
    click.echo(f"{'Ray id':40s} - {'ref':20s} - {'ts':20s}")

    for peep in resp["refs"]:
        click.echo(f"{peep['ray_id']:40s} - {peep['ref']:20s} - {peep['ts']:20s}")


ref.add_command(ls)

if __name__ == "__main__":
    ref()
