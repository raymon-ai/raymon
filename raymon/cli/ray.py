import json
import click
import yaml
import requests
import msgpack
from raymon.loggers import RaymonAPI


@click.group()
def ray():
    pass


@click.command()
@click.option("--project-id", help="The name of the project you want to list the rays for")
def ls(project_id):
    api = RaymonAPI(url="http://localhost:8000")
    api.login()
    params = {"project_id": project_id}
    resp = api.get(route=f"ray", params=params).json()
    click.echo(f"{'Ray id':40s} {'Last update':20s}")

    for ray in resp["rays"]:

        click.echo(f"{ray['ray_id']:40s} {ray['ts']:20s}")


ray.add_command(ls)

if __name__ == "__main__":
    ray()
