from raymon.profiling.extractors.vision import Sharpness
from raymon.tests.conftest import load_data


def test_extract(load_data):
    assert isinstance(Sharpness().extract(load_data[0]), float)


def test_extract_multiple(load_data):
    avg_intensity_list = Sharpness().extract_multiple(load_data)
    assert isinstance(avg_intensity_list, list)
    assert isinstance(avg_intensity_list[0], float)


def test_to_jcr():
    jcr = Sharpness().to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.vision.sharpness.Sharpness"
    assert not jcr["state"]


def test_from_jcr():
    extractor = Sharpness()
    jcr = extractor.to_jcr()
    assert isinstance(extractor.from_jcr(jcr), Sharpness)


def test_build(load_data):
    assert not Sharpness().build(load_data[0])


def test_is_built():
    assert Sharpness().is_built()
