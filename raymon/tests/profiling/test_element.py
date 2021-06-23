#%%
from raymon.profiling.extractors.structured import ElementExtractor, generate_components
from raymon.profiling.components import InputComponent
from raymon.tests.conftest import load_data
import pandas as pd


def test_element():
    extractor = ElementExtractor(3)
    extractor.element = 4
    assert extractor.element == 4


def test_extract(load_data):
    extractor = ElementExtractor(3)
    assert extractor.extract(load_data) == load_data[3]


def test_to_jcr():
    extractor = ElementExtractor(3)
    jcr = extractor.to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.structured.element.ElementExtractor"
    assert jcr["state"]["element"] == 3


def test_from_jcr():
    extractor = ElementExtractor(3)
    jcr = extractor.to_jcr()
    other_extractor = extractor.from_jcr(jcr)
    assert other_extractor.element == 3


def test_build(load_data):
    extractor = ElementExtractor(3)
    extractor.build(load_data)


def test_is_built():
    extractor = ElementExtractor(3)
    assert extractor.is_built()


def test_str():
    extractor = ElementExtractor(3)
    assert str(extractor) == "ElementExtractor(element=3)"


def test_generate_components():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
        "cat2": ["c"] * 5 + ["d"] * 5,
        "num2": [0.2] * 10,
    }
    df = pd.DataFrame(data=cols)
    components = generate_components(dtypes=df.dtypes, complass=InputComponent)
    assert len(components) == 4
    assert components[1].name == "cat1"
    assert components[0].dtype == "INT"
    assert components[1].dtype == "CAT"
    assert components[3].dtype == "FLOAT"
    assert components[0].extractor.element == "num1"
