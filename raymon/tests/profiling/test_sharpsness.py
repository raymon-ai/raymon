from raymon.profiling.extractors.vision import Sharpness
from raymon.tests.conftest import load_data


def test_extract(load_data):
    extractor = Sharpness()
    assert isinstance(extractor.extract(load_data[0]), float)


def test_extract_multiple(load_data):
    extractor = Sharpness()
    avg_intensity_list = extractor.extract_multiple(load_data)
    assert isinstance(avg_intensity_list, list)
    assert isinstance(avg_intensity_list[0], float)


def test_to_jcr():
    extractor = Sharpness()
    jcr = extractor.to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.vision.sharpness.Sharpness"
    assert not jcr["state"]


def test_from_jcr():
    extractor = Sharpness()
    jcr = extractor.to_jcr()
    assert isinstance(extractor.from_jcr(jcr), Sharpness)


def test_build(load_data):
    extractor = Sharpness()
    assert not extractor.build(load_data[0])


def test_is_built():
    extractor = Sharpness()
    assert extractor.is_built()
