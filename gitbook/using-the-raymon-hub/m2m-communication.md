# M2M communication

Most of the examples in the Raymon docs require you to log in to Raymon when executing the code. The code is then authenticated as you, a user. This is not always a good approach. For example, your production system that constantly processed data, and that may be a shared responsibility between multiple people should not be authenticated a a user, but as an application. Raymon supports this.

### Creating a machine 2 machine app

First, you need to create an machine2machine app as shown below. This will save the m2m credentials as a JSON file.&#x20;

```python
from pathlib import Path
from raymon import RaymonAPI

from raymon.auth import m2m
from raymon.auth import DEFAULT_ENV

api = RaymonAPI(url=f"https://api.raymon.ai/v0")

resp = api.project_m2mclient_get(project_id="4854ecdf-725e-4627-8600-4dadf1588072")
if resp.ok:
    print(f"M2M creds found")
    m2mcreds = resp.json()
else:
    print(f"Creating m2m creds")
    resp = api.project_m2mclient_add(project_id="4854ecdf-725e-4627-8600-4dadf1588072")
    m2mcreds = resp.json()

outpath = (Path(".") / "m2mcreds-demo-retinopathy.json").resolve()

print(f"Saving creds to {outpath.resolve()}")

m2m.save_m2m_config(
    existing={},
    project_id="4854ecdf-725e-4627-8600-4dadf1588072",
    auth_endpoint=DEFAULT_ENV["auth_url"],
    audience=DEFAULT_ENV["audience"],
    client_id=m2mcreds["4854ecdf-725e-4627-8600-4dadf1588072"]["client_id"],
    client_secret=m2mcreds["4854ecdf-725e-4627-8600-4dadf1588072"]["client_secret"],
    grant_type="client_credentials",
    out=outpath,
)
```

### Using the machine 2 machine app

To authenticate as an application, create the Raymon API object as follows:

```python
api = RaymonAPI(
    url=f"https://api.raymon.ai/v0",
    project_id="4854ecdf-725e-4627-8600-4dadf1588072",
    auth_path=outpath,
)
```

It's important to note here that an m2m app is always tied to a project id. It only has access to that specific project id. Not specifying the project id when construction the API object will prompt you to authenticate as user.&#x20;
