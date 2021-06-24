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
    assert ElementExtractor(3).extract(load_data) == load_data[3]


def test_to_jcr():
    jcr = ElementExtractor(3).to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.structured.element.ElementExtractor"
    assert jcr["state"]["element"] == 3


def test_from_jcr():
    extractor = ElementExtractor(3)
    assert extractor.from_jcr(extractor.to_jcr()["state"]).element == 3


def test_build(load_data):
    ElementExtractor(3).build(load_data)


def test_is_built():
    assert ElementExtractor(3).is_built()


def test_str():
    assert str(ElementExtractor(3)) == "ElementExtractor(element=3)"


def test_generate_components():
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
        "cat2": ["c"] * 5 + ["d"] * 5,
        "num2": [0.2] * 10,
    }
    df = pd.DataFrame(data=cols)
    components = generate_components(dtypes=df.dtypes, complass=InputComponent, name_prefix="raymon_")
    assert len(components) == 4
    assert components[1].name == "raymon_cat1"
    assert components[0].dtype == "INT"
    assert components[1].dtype == "CAT"
    assert components[3].dtype == "FLOAT"
    assert components[0].extractor.element == "num1"
