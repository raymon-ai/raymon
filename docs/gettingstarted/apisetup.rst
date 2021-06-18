=============
Using the API
=============
The Raymon backend supports communication through a REST API, and provides the :class:`raymon.RaymonAPI` class to communicate with it.

To initialize the api, simply create an instance of the API class, with the API URL as parameter.

.. code-block:: python
  :linenos:

  from raymon import RaymonAPI

  api = RaymonAPI(url="https://api.raymon.ai/v0")

When executing the code snippet above, you will be asked to login to the Raymon platform through the browser. Once Logged in, you can use the api to interact with the Raymon backend. See :class:`raymon.RaymonAPI` for an overview of the available methods. Some frequently used ones are listed below.


Creating a project with the API
-------------------------------
Once logged in, you can create a project, just like we already did through the web UI. This returns a `project_id`, which needs to be passed in all api calls for that project.

.. code-block:: python
  :linenos:

  resp = api.project_create(project_name="tutorial_profile")
  project = resp.json()
  project_id = project["project_id"]



Setting the project manifest
----------------------------
Configuring the Raymon backend for a certain project is done using a project manifest yaml file (see :ref:`The project manifest` for more information). This manifest can be set as follows. 

.. code-block:: python
  :linenos:

  with open("manifest.yml", "r") as f:
      cfg = f.read()

  resp = api.orchestration_apply(project_id=project_id, cfg=cfg)


Uploading a model profile
-------------------------

The :class:`raymon.ModelProfile` is used to capture a model's input, output and actual data characteristics and perform data validation and tagging (see :ref:`Model & Data Profiling`. You can add a model profile to a project as follows:

.. code-block:: python
  :linenos:

  from raymon import ModelProfile

  profile = ModelProfile.load("profile.json")
  resp = api.profile_create(project_id=project_id, profile=profile)
  resp.json()

Adding a model profile to a project will automatically set up data quality and model performance monitoring. See :ref:`Model & Data Profiling` for more information.
