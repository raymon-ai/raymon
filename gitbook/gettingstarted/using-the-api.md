# Using the API

## Using the API[¶](using-the-api.md#using-the-api)

The Raymon backend supports communication through a REST API, and provides the [`raymon.RaymonAPI`](../module/raymonapi-class.md#raymon.RaymonAPI) class to communicate with it.

To initialize the api, simply create an instance of the API class, with the API URL as parameter.

|  |  |
| :--- | :--- |


When executing the code snippet above, you will be asked to login to the Raymon platform through the browser. Once Logged in, you can use the api to interact with the Raymon backend. See [`raymon.RaymonAPI`](../module/raymonapi-class.md#raymon.RaymonAPI) for an overview of the available methods. Some frequently used ones are listed below.

### Creating a project with the API[¶](using-the-api.md#creating-a-project-with-the-api)

Once logged in, you can create a project, just like we already did through the web UI. This returns a project\_id, which needs to be passed in all api calls for that project.

|  |  |
| :--- | :--- |


### Setting the project orchestration[¶](using-the-api.md#setting-the-project-orchestration)

Configuring the Raymon backend for a certain project is done using a project orchestration yaml file \(see [Backend Configuration](backend-configuration.md#backend-configuration) for more information\). This orchestration can be set as follows.

|  |  |
| :--- | :--- |


### Uploading a model profile[¶](using-the-api.md#uploading-a-model-profile)

The [`raymon.ModelProfile`](../module/modelprofile.md#raymon.ModelProfile) is used to capture a model’s input, output and actual data characteristics and perform data validation and tagging \(see [Model & Data Profiling](model-and-data-profiling.md#model-data-profiling). You can add a model profile to a project as follows:

|  |  |
| :--- | :--- |


Adding a model profile to a project will automatically set up data quality and model performance monitoring. See [Model & Data Profiling](model-and-data-profiling.md#model-data-profiling) for more information.

