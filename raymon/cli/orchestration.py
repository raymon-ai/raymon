import json
import click
import yaml
import requests
from raymon.loggers import RaymonAPI


@click.group()
def orchestration():
    pass


@click.command()
@click.option("--project-id", help="The project ID you want to apply the config to")
@click.option("--fpath", type=click.File("r"), help="File path to the config file. yaml.")
def apply(project_id, fpath):
    api = RaymonAPI(url="http://localhost:8000")
    api.login()
    cfg = {}
    # with open(fpath, 'r') as fp:
    cfg = json.dumps(yaml.full_load(fpath), indent=4)

    req_data = {"project_id": project_id, "cfg": cfg}
    resp = api.post(route="orchestration", data=req_data)
    click.echo(f"New orchestration for project {project_id}: {resp}")


@click.command()
@click.option("--project-id", help="The project ID you want to apply the config to")
def get(project_id):
    api = RaymonAPI(url="http://localhost:8000")
    api.login()
    params = {"project_id": project_id}
    resp = api.get(route=f"orchestration", params=params)
    cfg = resp.json()["cfg"]
    output = yaml.dump(json.loads(cfg))
    click.echo(output)


orchestration.add_command(apply)
orchestration.add_command(get)

if __name__ == "__main__":
    orchestration()
