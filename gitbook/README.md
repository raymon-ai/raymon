---
description: Quick intro to the Raymon library.
---

# Intro & Installation

![Raymon: analyse data &amp; model health](.gitbook/assets/image.png)

## What is Raymon?

**Raymon helps Machine Learning teams analyse data, data health and model performance.** Using data profiles, users can extract features describing data quality, data novelty, model confidence and prediction performance from data.Then, they can use these features to validate production data and monitor for data drift, data degradation and model degradation. 

**Raymon is open source and can be used standalone** but integrates nicely with the rest of the Raymon.ai ML Observability hub, for example to make predictions [traceable and debuggable](tracing-predictions/untitled.md).  


**Raymon’s focus is on simplicity and extendability**. We offer a set of extractors that are cheap to compute and simple to understand. Currently, we offer extractors for structured data and vision data, but you can easily implement you own extractor which means we can any data type and any extractor that you want. 

## Installation

You can install the open source Python client library from pip.

```text
pip install raymon
```

  
The library can be used standalone, but integrates nicely with the rest of the Raymon.ai platform. See [https://raymon.ai](https://raymon.ai) for more info.



