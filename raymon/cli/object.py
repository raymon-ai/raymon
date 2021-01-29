import json
import click
import yaml
import requests
import msgpack
from raymon.loggers import RaymonAPI


@click.group()
def result():
    pass


@click.command()
@click.option("--result-id", help="The name of the project you want to list the rays for")
def get(result_id):
    api = RaymonAPI(url="http://localhost:8000")
    api.login()
    params = {"object_id": result_id}
    resp = api.get(route=f"object", params=params).json()
    obj = resp["object"]
    click.echo(f"Type: {obj['type']}, data:\n {obj['params']['data']}")


result.add_command(get)
