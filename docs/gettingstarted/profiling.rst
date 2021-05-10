=============================
Data Profiling and Validation
=============================

One of the primary functionalities of Raymon is to help you validate and monitor production data quality. This is done using the :py:class:`raymon.ModelProfile` class. 

----------------------------------------------------
Concepts: Profiles, Components, Extractors and Stats
----------------------------------------------------

Raymon helps you capture data characterisics of your models inputs, outputs, actuals and scores using the :class:`raymon.ModelProfile` class. For each data profiling hook, a :class:`raymon.ModelProfile` contains a list of one or more components (:class:`raymon.Component`), each of which watches a feature of your data that is extracted from the data by the component using an :class:`raymon.Extractor`. Extractors can ingest any type of data (structured data, images, time series, ...) and return any feature as long as it is a single numerical or catagorical value (meaning, no vectors). For example, in case of structured data, an extractor may simply extract one element from its input vector, it may calculate the vector norm, or the norm of a subvector, etc... For image data, an extractor could extract an anomaly score, or it could extract the image sharpness. Each component saves statistics about its extracted feature in its stats property (:class:`raymon.Stats`). These stats will be used to validate new data.

As illustrted in the examples below, constructing a ModelProfile should be done at train time using :code:`profile.build(input=loaded_data)`. Then, the profile can be loaded in your production code and used to validate incoming data, for example as follows: :code:`profile.validate_input(data)`. Validating data will return several tags: the value the extractor returned, and optional error tags if the data is determined to have issues.


Profile
-------

Raymon currently has one type of profile: the :class:`raymon.ModelProfile` class. This class can be used to validate and score all data relevant to ML models (its inputs, outputs, actuals and scores) and can auto-configure the Raymon backend for model monitoring. 


Profile Components
------------------
A profile component is responsible for extracting a feature from the data it is given and to distill statistics about that extracted feature. The extrating of the feature is delegated to its :code:`extractor` property, the distillation of stats to its :code:`stats` property. Depending on the type (:code:`int`, :code:`float` or :code:`str`) an extractor returns, the component needs to be of the equivalent type: :class:`raymon.FloatComponent`, :class:`raymon.IntComponent`, :class:`raymon.CategoricComponent`. 



Component Extractors
--------------------
Extractors take in a datum and extract a feature from it. Raymon provides some out-of-the-box extractors, but you can easily plug in your own by implementting the :class:`raymon.SimpleExtractor` or :class:`raymon.ScoringExtractorExtractor` interface. Extractors convert your data to single value that Raymon will track. By doing so, Raymon in itself does not analyse your raw data and can support any data type.


Component Stats
---------------
For numeric components, :class:`raymon.NumericStats` tracks the min, max, mean, std, distribution and amount of invalid values of the component. For categoric components, :class:`raymon.CategoricStats` tracks the value frequencies and amount of invalid values. 

------------------------
Example: Vision Data
------------------------

.. code-block:: python
    :linenos:

    profile = ModelProfile(
            name="retinopathy",
            version="1.0.0",
            input_components=[
                FloatComponent(name="sharpness", extractor=Sharpness()),
                FloatComponent(name="intensity", extractor=AvgIntensity()),
                FloatComponent(name="outlierscore", extractor=DN2AnomalyScorer(k=20, size=(512, 512)))
            ],
        )
    # Build the profile
    profile.build(input=loaded_data)
    fullprofile_path = "../models/profile-retinopathy-1.1.0.json"
    profile.save(fullprofile_path)
    # reload the profile and validate some data
    profile = ModelProfile().load(fullprofile_path)
    tags = profile.validate_input(loaded_data[-1])


This code snippet above illustrates how one can define some checks on image data. Here, only the input data is checked.

------------------------
Example: Structured Data
------------------------

.. code-block:: python
    :linenos:

    from raymon.profiling import ModelProfile, FloatComponent
    from raymon.profiling.extractors.structured import generate_components, ElementExtractor
    from raymon.profiling.extractors.structured.scoring import AbsoluteError, SquaredError

    profile = ModelProfile(
        name="HousePriceModelProfile",
        version="1.0.0",
        input_components=generate_components(X.dtypes),
        output_components=[
            FloatComponent(name="prediction", extractor=ElementExtractor(element=0))
        ],
        actual_components=[
            FloatComponent(name="actual", extractor=ElementExtractor(element=0))
        ],
        score_components=[
            FloatComponent(name="abs_error", extractor=AbsoluteError()),
            FloatComponent(name="sq_error", extractor=SquaredError()),
        ],
    )
    profile.build(input=X, output=y_pred[None, :], actual=y_test[None, :])
    profile.save(ROOT / "models/profile-houseprices-v3.0.0.json")


This example, for structured data shows how one can define checks on inputs (tracking every element in the input vector), outputs and actuals, as well as defining scores we want to track. 