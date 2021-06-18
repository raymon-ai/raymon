.. Raymon documentation master file, created by
   sphinx-quickstart on Tue May  4 16:15:29 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Raymon: Observability for ML systems
============================================
Raymon is an observability platform for ML-based systems that requires minimal setup. It allows you to monitor data quality and model performance over multiple slices of your data, it alerts you when something is wrong and provides you with troubleshooting tooling for further anaysis. It is very extensible and it can serve for all data and model types.

Raymon's functionality includes:

- Making all model predictions and their pre- and postprocessing steps traceable.
- Validating incoming data and guarding for data drift or data health issues.
- Monitoring your model performance
- Benchmarking different slices of your production data against each other to expose sliced with reduced performance.
- Alerting when things break down
- Fetching production data for further debugging
- Exporting valuable data from production for building high-quality datasets and improving your models


---------------
Raymon overview
---------------
Raymon consists out of a client library and a backend. The client library (Python) needs to be integrated in your production code and will send data to the backend. The backend will process the data it receives and provide monitoring, alerting and troubleshooting functionality. 

The backend runs on Docker (Swarm mode) or Kubernetes and can be deployed on-premise, in your VPC or can be managed by us. The backend also provides a REST api and a Web UI for users to interact with.

---------
Quick FAQ
---------

......................
What is Observability?
......................
Wikipedia defines Observability as follows:

   Observability is a measure of how well internal states of a system can be inferred from knowledge of its external outputs.

Raymon helps you log, store, process and retrieve any info or data that you might need to verfiy your systems are healthy or to determine what is wrong. It aims to be a full solution for all monitoring and troubleshooting tailored for ML-powered systems. 


..................
Is it open source?
..................
Partly. Any code that needs to be integrated in your deployment (the client library used for logging and data profiling) is MIT licensed. However, our backend is not open source at this point. 


-----------------
Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   
   gettingstarted/landing
   api/apilanding





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
