import requests

from raymon.auth import login

MB = 1000000


class RaymonAPI:
    def __init__(self, url="http://localhost:8000", project_id=None, auth_path=None):
        self.project_id = project_id
        self.url = url
        self.auth_path = auth_path

        self.session = requests.Session()
        self.headers = {"Content-type": "application/json"}
        self.token = None

        self.login()

    """
    Functions related to Authentication
    """

    def login(self):
        self.token = login(fpath=self.auth_path, project_id=self.project_id)
        self.headers["Authorization"] = f"Bearer {self.token}"

    """HTTP METHODS"""

    def post(self, route, json=None, params=None):
        resp = self.session.post(
            f"{self.url}/{route}",
            json=json,
            params=params,
            headers=self.headers,
        )
        return resp

    def put(self, route, json=None, params=None):
        resp = self.session.put(
            f"{self.url}/{route}",
            json=json,
            params=params,
            headers=self.headers,
        )
        return resp

    def get(self, route, json=None, params=None):
        resp = self.session.get(
            f"{self.url}/{route}",
            json=json,
            params=params,
            headers=self.headers,
        )
        return resp

    def delete(self, route, json=None, params=None):
        resp = self.session.delete(
            f"{self.url}/{route}",
            json=json,
            params=params,
            headers=self.headers,
        )

        return resp

    """API methods"""

    def project_create(self, project_name):
        project_data = {"project_name": project_name}
        return self.post(route="projects", json=project_data)

    def project_search(self, project_name):
        project_data = {"project_name": project_name}
        return self.get(route="projects/search", params=project_data)

    def projects_ls(self):
        return self.get(route="projects")

    def project_m2mclient_add(self, project_id):
        return self.post(route=f"projects/{project_id}/m2m", json=None)

    def project_m2mclient_get(self, project_id):
        return self.get(route=f"projects/{project_id}/m2m", json=None)

    def project_transfer(self, project_id, user_id, org_id):
        # Either user_id or org_id should be None
        owner = {"user_id": user_id, "org_id": org_id}
        return self.put(route=f"projects/{project_id}", json=owner)

    def orchestration_apply(self, project_id, cfg):
        data = {"config": cfg}
        resp = self.put(route=f"projects/{project_id}", json=data)
        return resp

    def org_create(self, org_id, description):
        org = {"org_id": org_id, "description": description}
        return self.post(route="orgs", json=org)

    def org_get(self, org_id):
        return self.get(route=f"orgs/{org_id}")

    def org_add_user(self, org_id, user_id, user_readable):
        org = {"user_id": user_id, "user_readable": user_readable}
        return self.post(route=f"orgs/{org_id}/users", json=org)

    def org_rm_user(self, org_id, user_id):
        data = {"user_id": user_id}
        return self.delete(route=f"orgs/{org_id}/users", json=data)

    def schema_create(self, project_id, schema):
        schema_jcr = schema.to_jcr()
        schema_name = schema.name
        schema_version = schema.version
        return self.post(route=f"projects/{project_id}/schemas/{schema_name}/{schema_version}", json=schema_jcr)

    def schema_ls(self, project_id):
        return self.get(route=f"projects/{project_id}/schemas")

    def schema_get(self, project_id, schema_name, schema_version):
        return self.get(route=f"projects/{project_id}/schemas/{schema_name}/{schema_version}")

    def schema_reduce(self, project_id, schema_name, schema_version, begin, end, slicestr):
        params = {"begin": begin, "end": end, "slicestr": slicestr}
        return self.get(route=f"projects/{project_id}/schemas/{schema_name}/{schema_version}/reduce", params=params)

    def ray_ls(self, project_id, slicestr, begin, end, limit=250):
        params = {"begin": begin, "end": end, "slicestr": slicestr, "lim": limit}
        return self.get(route=f"projects/{project_id}/rays", params=params)

    def ray_get(self, project_id, ray_id):
        return self.get(route=f"projects/{project_id}/rays/{ray_id}")

    def object_ls(self, project_id, peephole, slicestr, begin, end, limit=250):
        params = {"begin": begin, "end": end, "slicestr": slicestr, "lim": limit, "peephole": peephole}
        return self.get(route=f"projects/{project_id}/objects", params=params)

    def object_get(self, project_id, object_id):
        return self.get(route=f"projects/{project_id}/objects/{object_id}")

    def object_search(self, project_id, ray_id, peephole):
        params = {
            "ray_id": ray_id,
            "peephole": peephole,
        }
        return self.get(route=f"projects/{project_id}/objects/search", params=params)

    def peepholes_ls(self, project_id, slicestr, begin, end, limit=250):
        params = {"begin": begin, "end": end, "slicestr": slicestr, "lim": limit}
        return self.get(route=f"projects/{project_id}/peepholes", params=params)

    def tags_ls(self, project_id):
        return self.get(route=f"projects/{project_id}/tags")

    def tags_get(self, project_id, ray_id):
        return self.get(route=f"projects/{project_id}/rays/{ray_id}/tags")
