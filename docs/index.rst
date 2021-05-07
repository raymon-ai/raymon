.. Raymon documentation master file, created by
   sphinx-quickstart on Tue May  4 16:15:29 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Raymon: Observability for ML-powered systems
============================================
Raymon is an observability platform tailored for ML systems. It helps you monitor data quality and model performance, it alerts you when something is wrong and provides you with troubleshooting tooling for complex systems.  It is heaviliy extensible and it can serve for all data and model types.

---------------
Raymon overview
---------------

Raymon consists out of a client library and a backend. The client library (Python) needs to be integrated in your code and will send data to the backend through direct API calls or logging to textfiles (that you then need to ship to the backend). The backend will process the data it receives and provide monitoring, alerting and troubleshooting functionality. 

The backend runs on Kubernetes and can be deployed on-premise, in your VPC or can be managed by us. The backend also provides a REST api and a Web UI for users to interact with.

---------
Quick FAQ
---------

......................
What is Observability?
......................
Wikipedia defines Observability as follows:

   Observability is a measure of how well internal states of a system can be inferred from knowledge of its external outputs.

Raymon helps you log, store, process and retrieve any info or data that you might need to verfiy your systems are healthy or to determine what is wrong. It aims to be a full solution for all monitoring and troubleshooting tailored for ML-powered systems. 

............................................................
What is "Observability for ML systems" and why do I need it?
............................................................
People often say that the most important part of being a data scientist is knowing your data. We fully agree, but would like to point out that the data that really matters is your production data, not your nicely cleaned, fixed training set.

A lot can go wrong in ML systems post-deployment without ML teams noticing due to the often silent nature of failures in ML. Data can start to drift due to changing behavior patterns, data quality can degrade and ranges can suddenly change due to changes in upsteam processing, changes in services you depend on or changes in how your clients call your systems. Often times, ML systems do not crash when this happens but still deliver a prediction, albeit of degraded quality. 

Finding out about issues like model degradation, data drift and data quality issues can be hard and exremely time consuming, as can deugging specific model predictions or finding out for what data exactly your system suffers from reduced performance. For example, in a system serving multiple clients, it may be hard to find out out that one specific client that accounts for 5% of the traffic has updated his frontend, and is now querying your system with data that contains much more invalid vlaues than before, resulting in predictions of lower quality than promised.

Raymon helps you find out about things like the above. In short, Raymon helps you with the following:
- Making all model predictions and their pre- and postprocessing steps traceable.
- Validating incoming data and guarding for data drift or data health issues.
- Monitoring your model performance, both by using incoming actuals or by validating your model outputs.
- Benchmarking different slices of your production data against each other to help you find out which suffer from reduced performance.
- Setting up alerting when things break down
- Fetching relevant and valuable production data, either to debug a specific prediction or to improve your models by building high-quality datasets.
- A/B testing of models

...........................................................
How does Raymon differentiate from other tools like X or Y?
...........................................................

In our experience, teams often rely on open source tooling that was generally developed for traditional engineering use cases but, in our opinion, lacks functionality required for data-centric applications like ML systems. For example, ELK may be used to store logs and Grafana may be used to monitor certain metrics. We see several issues with using tools like this for ML monitoring and troubleshooting. 

First of all, regarding logging, text logs only say so much when debugging ML systems. Being able to easily trace your data, and its transforms during pre and postprocessing, over multiple microservices and combining this with (interactive) visualisations can speed up sanity checks and debugging workflows tremendously, which is exaclty what Raymon does.

Secondly, monitoring data and model metrics metrics generally leads to a huge amount of metrics to track. Doing this for several slices (like multiple clients) of production data independently leads to exponentially more metrics (and dashboards) to track. Moreover, setting up all of this takes a huge amount of time with traditional tooling. Finally, monitoring model performance with non-ML-tailored tooling genrally requires a lot of engineering work to ingest and store actuals somewhere, and to set up a system that combines predictions and actuals into performance metrics. With Raymon, we automate all of this, and alert you when something is wrong.

Because teams use different tools, often combined with in-house developed tooling, valuable links between the different tools are lost, which is detrimental to productivity. For example, going from a globally aggregated metric like model accuracy, to model accuracy for a specific client or to the data that leads to some extremely bad predictions can be a really cumbersome process. With Raymon you can easily slice and dice your production dashboards and go from global aggregates to slice aggregates and even to individial data points. 

Raymon is also heavily extensible and provides hooks that allow you to define your own visualizations and data processing.

..................
Is it open source?
..................
Partly. Any code that needs to be integrated in your deployment (the client library used for logging and data profiling) is MIT licensed. However, our backend is not open source at this point (yet?). We do offer free licenses for small teams and trial periods though. Please check out our `website <https://raymon.ai>`_ to find out more.

-----------------
Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   install_deploy
   logging_tracing


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
