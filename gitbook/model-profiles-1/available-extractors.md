---
description: This page lists the available extractors in Raymon
---

# Extractors in detail

Extractors give Raymon a lot of flexibility. Raymon currently comes with a \(small\) set of out-of-the-box extractors, but we are always looking to add more. If you are missing functionality, you can write your own extractor, or let us know through the [Github issues](https://github.com/raymon-ai/raymon/issues), and we can look into implementing it and shipping it with the open source library.

## Extractor interface

All extractors must be subclasses of either `raymon.profiling.extractors.SimpleExtractor` or `raymon.profiling.extractors.EvalExtractor`. The `SimpleExtractor` is used to extract a feature from a single input like the profile's input, output or actuals. The `EvalExtractor` is used to extract a feature from the combination of an output with and actual, hence evaluating a mode prediction.

 All subclasses must implement the `extract` method, which depending on the type takes in 1 or 2 parameters, as described above. The method signatures are as follows:

```python
class SimpleExtractor(Extractor):
    @abstractmethod
    def extract(self, data):
        """Extracts a component from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a component from. The type is up to you.

        """
        raise NotImplementedError


class EvalExtractor(Extractor):
    @abstractmethod
    def extract(self, output, actual):
        """Extracts a component from a data instance.

        Parameters
        ----------
        data : any
            The data instance you want to extract a component from. The type is up to you.

        """
        raise NotImplementedError
```

For more information about the dataflow when using profiles and extractors, see [this page](concepts-and-building-flow.md).

## Extractor List

The \(currently limited\) set of available extractors are linked below. More extractors & docs are coming.

### General / structured data focus

| Name | Compatibility | Notes |
| :--- | :--- | :--- |
| `ElementExtractor` | input, output, actual | This extractor simply extracts an element from an array, series or dict. [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/structured/element.py#L8). |
| `MaxScoreElementExtractor` | input, output, actual | Extract the index with the maximum value from a vector, and optionally translate it to a categorical value if categories are given. [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/structured/element.py#L58). |
| `KMeansOutlierScorer` | input, output, actual | Clusters the data at building time and generates a data novelty score at validation time. [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/structured/kmeans.py#L11). |
| `IsolationForestOutlierScorer` | input, output, actual | Builds an isolation forest at building time and generates an outlier score at validation time. [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/structured/iforest.py#L13). |
| `ClassificationEntropyExtractor` | output | Takes the output of a classifier \(i.e. a vector of probabilities\) and extracts the entropy. [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/structured/entropy.py#L7). |
| `ClassificationMarginExtractor` | output | Takes the output of a classifier \(i.e. a vector of probabilities\) and extracts the classification margin, which is the difference in probability between the most likely and the second most likely class. [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/structured/margin.py#L7). |

### Vision focus

| Name  | Compatibility | Notes |
| :--- | :--- | :--- |
| `AvgIntensity` | input | Extract the average intensity from an image. [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/vision/intensity.py#L7). |
| `Sharpness` | input | Extract a sharpness metric from an image. [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/vision/sharpness.py#L7). |
| `FixedSubpatchSimilarity` | input | Extracts a metric of how similar a certain region of the image is to a set of references. Useful in setups where a certain element should always be visible. Requires extractor building. [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/vision/similarity.py#L11). |
| `DN2AnomalyScorer` | input | Extracts a data novelty metric based on the similarity to reference images. Based on a neural feature extractor and the `KMeansOutlierScorer`. Requires extractor building. [Paper](https://arxiv.org/abs/2002.10445). [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/vision/anomaly.py#L15). |
| `YoloConfidenceExtractor` | output | Given the output of the [PyTorch-YOLOv3](https://github.com/eriklindernoren/PyTorch-YOLOv3) object detector, this will extract the min, max or mean object detection confidence per image. [Paper](https://arxiv.org/abs/1809.09875). [Source](https://github.com/raymon-ai/raymon/blob/71e1e5455d69e01cb9e19dd60d5012997caa9e8c/raymon/profiling/extractors/vision/yolo.py#L6).  |

## Extractor preprocessing

There are a few special extractor wrappers. They allow you to execute some preprocessing before the extractor. This is useful to do some data transformation before the extractor runs. 

<table>
  <thead>
    <tr>
      <th style="text-align:left">Name</th>
      <th style="text-align:left">Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align:left"><code>SequenceSimpleExtractor</code>
      </td>
      <td style="text-align:left">Allows you to run preprocessing before running an extractor. Source.</td>
    </tr>
    <tr>
      <td style="text-align:left"><code>SequenceEvalExtractor</code>
      </td>
      <td style="text-align:left">
        <p>Allows you to run preprocessing before running an EvalExtractor. Source.</p>
        <p></p>
      </td>
    </tr>
  </tbody>
</table>

## Writing your own

Extractors are always executed in code that you control, never on our backend. This means you can easily plug in your own. All you need to do is implement the `raymon.profiling.extractors.SimpleExtractor` or `raymon.profiling.extractors.EvalExtractor interface!`



