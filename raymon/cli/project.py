import json
import click
import yaml
import requests
import msgpack
from raymon.loggers import RaymonAPI


@click.group()
def project():
    pass


@click.command()
@click.option("--project-name", help="The name of the project you want to create")
def create(project_name):
    api = RaymonAPI(url="http://localhost:8000")
    api.login()

    req_data = {
        "project_name": project_name,
    }
    resp = api.post(route="project", data=req_data)
    project_id = resp.json()["project_id"]
    click.echo(f"New project created: {project_id}: {resp}")


@click.command()
def ls():
    api = RaymonAPI(url="http://localhost:8000")
    api.login()
    resp = api.get(route=f"project", params={})
    click.echo(f"found projects: ")
    for project in resp.json()["projects"]:
        click.echo(f"{project['name']:20s} - {project['id']:20s}")


project.add_command(create)
project.add_command(ls)

if __name__ == "__main__":
    project()
