# Model & Data Profiling

One of the primary functionalities of Raymon is to help you validate incoming data, monitor production data quality and be able to find valuable data easily. This is mainly done using the [`raymon.ModelProfile`](../module/modelprofile.md#raymon.ModelProfile) class, which does so by generating tags that can be pushed to the backend.

In short, Raymon analyses your data at training time and builds a data profile that can be sent to the backend and loaded in your production code. You can use the profile to validate incoming data, model predictions and model actuals, as well as to score model predictions. This will generate tags that are pushed to the backend. The backend will then use those tags to monitor data quality and trigger alerts when appropriate.

## Concepts: Profiles, Components, Extractors, Stats and Reducers[¶](model-and-data-profiling.md#concepts-profiles-components-extractors-stats-and-reducers)

Raymon helps you capture data characteristics of your models inputs, outputs, actuals and output-actual evaluations using the [`raymon.ModelProfile`](../module/modelprofile.md#raymon.ModelProfile) class.

### Profile[¶](model-and-data-profiling.md#profile)

A [`raymon.ModelProfile`](../module/modelprofile.md#raymon.ModelProfile) is the main entry point for data profiling in Raymon. It’s an object that has a name and a version, and holds a list of `raymon.profiling.Component` objects and a list of `raymon.profiling.Reducer` objects, both are which are further explained below.

Raymon currently has one type of profile: the [`raymon.ModelProfile`](../module/modelprofile.md#raymon.ModelProfile) class. This class can be used to validate and score all data relevant to ML models \(its inputs, outputs, actuals and output-actual evaluations\) and can auto-configure the Raymon backend for model & data monitoring.

### Profile Components[¶](model-and-data-profiling.md#profile-components)

A profile component is responsible for extracting a feature from the data it is given and to distill statistics about that extracted feature. The extraction of the feature is delegated to its `extractor` property, the distillation of stats to its `stats` property. When validating data, the extracted feature will be returned as a :raymon.Tag: object with the component’s `name` as tag `name` and the feature value as tag `value`.

A component can be one of 4 types.

### Component Stats[¶](model-and-data-profiling.md#component-stats)

`raymon.Stats` objects are responsible for storing statistics about extracted features. For numeric components, [`raymon.IntStats`](../module/stats.md#raymon.IntStats) and [`raymon.FloatStats`](../module/stats.md#raymon.FloatStats) track the min, max, mean, std, distribution and amount of invalid values seen during building. For categoric components, [`raymon.CategoricStats`](../module/stats.md#raymon.CategoricStats) tracks the value frequencies and amount of invalid values. Depending on the type \(`int`, `float` or `str`\) a component’s extractor returns, the component’s stats need to be of the equivalent type \([`raymon.IntStats`](../module/stats.md#raymon.IntStats), [`raymon.FloatStats`](../module/stats.md#raymon.FloatStats) or [`raymon.CategoricStats`](../module/stats.md#raymon.CategoricStats).

### Reducers[¶](model-and-data-profiling.md#reducers)

Reducers take in extracted features and reduce those to one or a fixed amount of scores. For example, a reducer could reduce all absolute errors of a given dataset into the mean absolute error, or could calculate a precision and recall score.

A reducer is of type `raymon.Reducer` and needs a `name`, `inputs` and `preferences` as initialization parameters. `inputs` designate the tags that the reducer should take as input, `preferences` indicate whether the value should be high or low for every output. For example, when reducing the `absolute_error` tag to the mean absolute error, the preference should be `low`, since a low error is better. When reducing a precision and recall score, the preference should be `high` for both outputs, since a higher score is better.

Reducers may seem cumbersome at first, but their main goal is to auto-configure the Raymon backend when a model profile is uploaded.

## Building profiles[¶](model-and-data-profiling.md#building-profiles)

Defining a model profile is done by first defining its structure and then building it with some data.

The code snippet below illustrates for to build a `ModelProfile` based on a `DataFrame`. As can be seen, the profile tracks all the model’s inputs, outputs, actuals and scores \(evaluations\). It also reduces the absolute error to the mean absolute error.

Note the use of the `raymon.profiling.extractors.structured.generate_components()` function on line 11. This method generates a component for every column in the input DataFrame.

|  |  |
| :--- | :--- |


More examples of building profiles can be found in the basic examples [here \(structured\)](https://github.com/raymon-ai/raymon/blob/master/examples/1-building_structured.ipynb) and [here \(vision\)](https://github.com/raymon-ai/raymon/blob/master/examples/2-building_cv.ipynb) and in full [demonstrator code](https://github.com/raymon-ai/examples) [here \(structured data\)](https://github.com/raymon-ai/demonstrators/blob/master/houseprices/houseprices/train_model.py#L174-L197) and [here \(vision data\)](https://github.com/raymon-ai/demonstrators/blob/master/retinopathy/retinopathy/train.py#L67-L114)

## Viewing profiles[¶](model-and-data-profiling.md#viewing-profiles)

As shown in the [examples](https://github.com/raymon-ai/raymon/blob/master/examples), raymon offers a simple UI for viewing model profiles and comparing a POI with the profile. The figure below show what that looks like, but the UI is interactive, so you should go try it out yourself!

## Validating data[¶](model-and-data-profiling.md#validating-data)

Validating inputs, outputs and actuals is done through calling , [`raymon.ModelProfile.validate_input()`](../module/modelprofile.md#raymon.ModelProfile.validate_input), [`raymon.ModelProfile.validate_output()`](../module/modelprofile.md#raymon.ModelProfile.validate_output), or [`raymon.ModelProfile.validate_actual()`](../module/modelprofile.md#raymon.ModelProfile.validate_actual). Validating evaluator components is done through [`raymon.ModelProfile.validate_eval()`](../module/modelprofile.md#raymon.ModelProfile.validate_eval). The model evaluation can also be done on the raymon backend, or through webhooks on the backend \(see [Backend Configuration](backend-configuration.md#backend-configuration)\).

|  |  |
| :--- | :--- |


Further examples can be found on lines [204](https://github.com/raymon-ai/demonstrators/blob/master/houseprices/houseprices/processing.py#L204), [219](https://github.com/raymon-ai/demonstrators/blob/master/houseprices/houseprices/processing.py#L219) and [250](https://github.com/raymon-ai/demonstrators/blob/master/houseprices/houseprices/processing.py#L250).

## Contrasting profiles[¶](model-and-data-profiling.md#contrasting-profiles)

As shown in the [examples](https://github.com/raymon-ai/raymon/blob/master/examples), Raymon also offers a simple UI to contrast 2 profiles. The figure below show how that looks like, but again, the report is interactive, so you should try it out yourself.

## Using profile to configure the backend[¶](model-and-data-profiling.md#using-profile-to-configure-the-backend)

Building model profiles at model train time should be easy, and could be useful without using the rest of the Raymon system. However, when attaching the model profile to a certain project, the Raymon backend automatically configures it’s data health checking functionality and will generate alerts when data or model performance issues are discovered.

How to upload a model profile to the backend is already shown in [Uploading a model profile](using-the-api.md#uploading-a-model-profile), but is repeated below.

|  |  |
| :--- | :--- |


