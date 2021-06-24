from raymon.profiling.extractors.structured import ElementExtractor, generate_components
from raymon.profiling.components import InputComponent
import pandas as pd
import numpy as np


def test_element():
    extractor = ElementExtractor(3)
    extractor.element = 4
    assert extractor.element == 4


def test_extract():
    vector1 = np.array([[10], [20], [30]])
    assert ElementExtractor(2).extract(vector1) == [30]
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
        "cat2": ["c"] * 5 + ["d"] * 5,
        "num2": [0.2] * 10,
    }
    assert ElementExtractor("num1").extract(cols) == list(range(10))


def test_to_jcr():
    jcr = ElementExtractor(3).to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.structured.element.ElementExtractor"
    assert jcr["state"]["element"] == 3


def test_from_jcr():
    extractor = ElementExtractor(3)
    assert extractor.from_jcr(extractor.to_jcr()["state"]).element == 3


def test_build(images):
    ElementExtractor(3).build(images)


def test_is_built():
    assert ElementExtractor(3).is_built()


def test_str():
    assert str(ElementExtractor(3)) == "ElementExtractor(element=3)"
