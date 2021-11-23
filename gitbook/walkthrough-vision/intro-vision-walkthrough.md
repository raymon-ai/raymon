---
description: Setting the scene for the walkthrough.
---

# Intro: vision walkthrough

This walkthrough gives a complete overview of the required steps to get started with Raymon. It uses the use case of a simplified computer vision project (with a mocked out model).

The code and data for this walkthrough can be found on Github [here](https://github.com/raymon-ai/raymon-demos/tree/master/retinopathy). You can go ahead and clone the repo to your local machine. Since it includes data, it can be rather big. For this use case, you'll use the contents of the `retinopathy` directory.

```bash
git clone git@github.com:raymon-ai/raymon-demos.git
cd raymon-demos/retinopathy
```

Next, you should install the demo (in editable mode) and its requirements:

```bash
pip install -e .
```

Installing in editable mode will make sure you can easily change the code during this walkthrough.

## What's next?

The walkthrough contains the following steps:

* Introducing the existing use case
* Integrating Raymon: data validation and data inspection
* Setting up monitoring with Raymon
* Setting up slice-based monitoring
* Issues & Tuning

