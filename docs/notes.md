# Types

Raymon offers basic types. Types must implement the fuunctions `to_json` and `from_json` so they can be serialized. Types are defined in the `raymon.types` module. you can register your own types at runtime by simply adding your type definition to `raymon.types.DTYPES`.

# OpenFaaS

### function building

- function folder and template folder are combined. function folder is called `function`. Then Dockerfile is run.
- There can be function-specific dependencies and template dependencies
- Raymon should have a template:
  - http based ( Falcon / Flask)
  - Function Logs are forwarded: https://www.devdungeon.com/content/python-use-stringio-capture-stdout-and-stderr
    - Capture stdout / stderr and return as value?
    - Capture function in complete exception?
  - pip configuration for private devpi server: https://pip.pypa.io/en/stable/user_guide/#environment-variables
    - `PIP_INDEX_URL=http://host.docker.internal:3141/raymon/dev`
    - `PIP_TRUSTED_HOST="pypi.orgfiles.pythonhosted.org download.pytorch.org host.docker.internal"`
    - Need to add them as `ARG` in `Dockerfile`
      - These need to passed as command-line arguments: `faas-cli up --build-arg PIP_INDEX_URL=http://host.docker.internal:3141/raymon/dev --build-arg PIP_TRUSTED_HOST="pypi.orgfiles.pythonhosted.org download.pytorch.org host.docker.internal"`
  - Other configuration: through environment variables **or secrets**
  - raymon lib (types) must be preinstalled
    - users must be able to load their own types: make them in a package and list them as dependency



### python3-*

- http: handler signature changes to take in context and event
- flask: same signature as normal tempaltes
- debian: for compiling dependencies



