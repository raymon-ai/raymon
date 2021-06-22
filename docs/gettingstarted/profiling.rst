======================
Model & Data Profiling
======================

One of the primary functionalities of Raymon is to help you validate incoming data, monitor production data quality and be able to find valuable data easily. This is mainly done using the :py:class:`raymon.ModelProfile` class, which does so by generating tags that can be pushed to the backend. 

In short, Raymon analyses your data at training time and builds a data profile that can be sent to the backend and loaded in your production code. You can use the profile to validate incoming data, model predictions and model actuals, as well as to score model predictions. This will generate tags that are pushed to the backend. The backend will then use those tags to monitor data quality and trigger alerts when appropriate.

--------------------------------------------------------------
Concepts: Profiles, Components, Extractors, Stats and Reducers
--------------------------------------------------------------

Raymon helps you capture data characteristics of your models inputs, outputs, actuals and output-actual evaluations using the :class:`raymon.ModelProfile` class. 


Profile
-------

A :class:`raymon.ModelProfile` is the main entry point for data profiling in Raymon. It's an object that has a name and a version, and holds a list of :class:`raymon.profiling.Component` objects and a list of :class:`raymon.profiling.Reducer` objects, both are which are further explained below. 

Raymon currently has one type of profile: the :class:`raymon.ModelProfile` class. This class can be used to validate and score all data relevant to ML models (its inputs, outputs, actuals and output-actual evaluations) and can auto-configure the Raymon backend for model & data monitoring. 


Profile Components
------------------
A profile component is responsible for extracting a feature from the data it is given and to distill statistics about that extracted feature. The extraction of the feature is delegated to its :code:`extractor` property, the distillation of stats to its :code:`stats` property. When validating data, the extracted feature will be returned as a :raymon.Tag: object with the component's :code:`name` as tag :code:`name` and the feature value as tag :code:`value`. 


A component can be one of 4 types.

.. list-table:: Component types and their function
   :widths: 25 75
   :header-rows: 1

   * - Component Type
     - Function
   * - :class:`raymon.InputComponent`
     - Used for capturing input data characteristics.
   * - :class:`raymon.OutputComponent`
     - Used for capturing output data characteristics.
   * - :class:`raymon.ActualComponent`
     - Used for capturing actual (ground truth) data characteristics.
   * - :class:`raymon.EvalComponent`
     - Used for capturing characteristics that depend on both outputs and actuals, like model performance scores.


Component Extractors
--------------------
Extractors take in a datum and extract a feature from it. Raymon provides some out-of-the-box extractors, but you can easily plug in your own by implementing the :class:`raymon.SimpleExtractor` or :class:`raymon.EvalExtractor` interface. Extractors convert your data (image, Pandas Series, ...) to single value (a tag) that Raymon will track. Since extractors only need to run in your code, and not on the raymon backend, Raymon can support any data type.

Extractors of :class:`raymon.SimpleExtractor` are suited for components of type :class:`InputComponent`, :class:`OutputComponent` and :class:`ActualComponent` and have a single value as input (i.e., the models, input, output or actual). Extractors of :class:`raymon.EvalExtractor` are only suited for components of type :class:`raymon.EvalComponent` and take in 2 arguments: the model output and the actual. 

A :class:`raymon.SimpleExtractor` can for example extract a specific dimension of a vector, the sharpness of an image or some anomaly score for a given datum. A :class:`raymon.EvalExtractor` could for example calculate the absolute error of a given prediction and actual.


Component Stats
---------------
:class:`raymon.Stats` objects are responsible for storing statistics about extracted features. For numeric components, :class:`raymon.IntStats` and :class:`raymon.FloatStats` track the min, max, mean, std, distribution and amount of invalid values seen during building. For categoric components, :class:`raymon.CategoricStats` tracks the value frequencies and amount of invalid values. 
Depending on the type (:code:`int`, :code:`float` or :code:`str`) a component's extractor returns, the component's stats need to be of the equivalent type (:class:`raymon.IntStats`, :class:`raymon.FloatStats` or :class:`raymon.CategoricStats`.


Reducers
--------
Reducers take in extracted features and reduce those to one or a fixed amount of scores. For example, a reducer could reduce all absolute errors of a given dataset into the mean absolute error, or could calculate a precision and recall score.

A reducer is of type :class:`raymon.Reducer` and needs a :code:`name`, :code:`inputs` and :code:`preferences` as initialization parameters. :code:`inputs` designate the tags that the reducer should take as input,  :code:`preferences` indicate whether the value should be high or low for every output. For example, when reducing the :code:`absolute_error` tag to the mean absolute error, the preference should be :code:`low`, since a low error is better. When reducing a precision and recall score, the preference should be :code:`high` for both outputs, since a higher score is better.

Reducers may seem cumbersome at first, but their main goal is to auto-configure the Raymon backend when a model profile is uploaded. 

-----------------
Building profiles
-----------------
Defining a model profile is done by first defining its structure and then building it with some data. 

The code snippet below illustrates for to build a :code:`ModelProfile` based on a :code:`DataFrame`. As can be seen, the profile tracks all the model's inputs, outputs, actuals and scores (evaluations). It also reduces the absolute error to the mean absolute error.

Note the use of the :meth:`raymon.profiling.extractors.structured.generate_components` function on line 11. This method generates a component for every column in the input DataFrame.

.. code-block:: python
    :linenos:

    from raymon.profiling import (
        ModelProfile,
        InputComponent,
        OutputComponent,
        ActualComponent,
        EvalComponent,
        MeanReducer,
    )
    from raymon.profiling.extractors.structured import generate_components, ElementExtractor

    components = generate_components(X.dtypes, compclass=InputComponent) + [
        OutputComponent(name="prediction", extractor=ElementExtractor(element=0)),
        ActualComponent(name="actual", extractor=ElementExtractor(element=0)),
        EvalComponent(name="abs_error", extractor=AbsoluteRegressionError()),
    ]
    reducers = [
        MeanReducer(
            name="MAE",
            inputs=["abs_error"],
            preferences={"mean": "low"},
            results=None,
        )
    ]

    profile = ModelProfile(
        name="HousePricesCheap",
        version="2.0.0",
        components=components,
        reducers=reducers,
    )
    profile.build(input=X, output=y_pred[None, :], actual=y_test[None, :])
    profile.save(ROOT / "models")


More examples of building profiles can be found in the basic examples `here (structured) <https://github.com/raymon-ai/raymon/blob/master/examples/1-building_structured.ipynb>`_ and `here (vision) <https://github.com/raymon-ai/raymon/blob/master/examples/2-building_cv.ipynb>`_ and in full `demonstrator code <https://github.com/raymon-ai/examples>`_ `here (structured data) <https://github.com/raymon-ai/demonstrators/blob/master/houseprices/houseprices/train_model.py#L174-L197>`_ and `here (vision data) <https://github.com/raymon-ai/demonstrators/blob/master/retinopathy/retinopathy/train.py#L67-L114>`_

----------------
Viewing profiles
----------------
As shown in the `examples <https://github.com/raymon-ai/raymon/blob/master/examples>`_, raymon offers a simple UI for viewing model profiles and comparing a POI with the profile. The figure below show what that looks like, but the UI is interactive, so you should go try it out yourself!

.. figure:: screens/profileview.png
  :width: 800
  :alt: Viewing a profile & poi.
  :class: with-shadow with-border


---------------
Validating data
---------------
Validating inputs, outputs and actuals is done through calling , :meth:`raymon.ModelProfile.validate_input`, :meth:`raymon.ModelProfile.validate_output`, or :meth:`raymon.ModelProfile.validate_actual`. Validating evaluator components is done through :meth:`raymon.ModelProfile.validate_eval`. The model evaluation can also be done on the raymon backend, or through webhooks on the backend (see :ref:`The project orchestration`).

.. code-block:: python
    :linenos:

    def process(self, req_id, data, metadata):
        trace = Trace(logger=self.raymon, trace_id=str(req_id))

        # validate data
        input_tags = self.profile.validate_input(input=data)
        trace.tag(input_tags)
        # ...
        pred_arr = self.model.predict(data)
        pred = float(pred_arr[0])
        output_tags = self.profile.validate_output(output=pred_arr)
        trace.tag(output_tags)


Further examples can be found on lines `204 <https://github.com/raymon-ai/demonstrators/blob/master/houseprices/houseprices/processing.py#L204>`_, `219 <https://github.com/raymon-ai/demonstrators/blob/master/houseprices/houseprices/processing.py#L219>`_ and `250 <https://github.com/raymon-ai/demonstrators/blob/master/houseprices/houseprices/processing.py#L250>`_. 

--------------------
Contrasting profiles
--------------------
As shown in the `examples <https://github.com/raymon-ai/raymon/blob/master/examples>`_, Raymon also offers a simple UI to contrast 2 profiles. The figure below show how that looks like, but again, the report is interactive, so you should try it out yourself.

.. figure:: screens/profilecompare.png
  :width: 800
  :alt: Comparing 2 profiles.
  :class: with-shadow with-border


--------------------------------------
Using profile to configure the backend
--------------------------------------
Building model profiles at model train time should be easy, and could be useful without using the rest of the Raymon system. However, when attaching the model profile to a certain project, the Raymon backend automatically configures it's data health checking functionality and will generate alerts when data or model performance issues are discovered.

How to upload a model profile to the backend is already shown in :ref:`Uploading a model profile`, but is repeated below.

.. code-block:: python
  :linenos:

  from raymon import ModelProfile

  profile = ModelProfile.load("profile.json")
  resp = api.profile_create(project_id=project_id, profile=profile)
  resp.json()
