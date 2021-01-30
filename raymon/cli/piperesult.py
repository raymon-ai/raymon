import json
import click
import yaml
import requests
import msgpack
from raymon.loggers import RaymonAPI


@click.group()
def piperesult():
    pass


@click.command()
@click.option("--project-id", help="The name of the project you want to list the rays for")
# @click.option('--ray-id', help='The ray id')
# @click.option('--peephole', help='the peepholes')
def ls(project_id):
    api = RaymonAPI(url="http://localhost:8000")
    api.login()
    params = {
        "project_id": project_id,
        #   'ray_id': ray_id,
        #   'peephole': peephole
    }
    resp = api.get(route=f"piperesult", params=params).json()
    click.echo(f"{'Ray id':40s} - {'peephole':20s} - {'pipeline':20s} - {'data_object_id':40s} - {'viz_object_id':40s}")
    for piperes in resp["results"]:
        click.echo(
            f"{piperes['ray_id']:40s} - {piperes['peephole']:20s} - {piperes['pipeline']:20s} - {piperes['data_object_id']:40s} - {piperes['viz_object_id']:40s}"
        )


piperesult.add_command(ls)

if __name__ == "__main__":
    piperesult()
