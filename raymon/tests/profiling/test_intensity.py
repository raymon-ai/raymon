from raymon.profiling.extractors.vision import AvgIntensity
from raymon.tests.conftest import load_data


def test_extract(load_data):
    assert isinstance(AvgIntensity().extract(load_data[0]), float)


def test_extract_multiple(load_data):
    avg_intensity_list = AvgIntensity().extract_multiple(load_data)
    assert isinstance(avg_intensity_list, list)
    assert isinstance(avg_intensity_list[0], float)


def test_to_jcr():
    jcr = AvgIntensity().to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.vision.intensity.AvgIntensity"
    assert len(jcr["state"]) == 0


def test_from_jcr():
    extractor = AvgIntensity()
    assert isinstance(extractor.from_jcr(extractor.to_jcr()), AvgIntensity)


def test_build(load_data):
    AvgIntensity().build(load_data[0])


def test_is_built():
    assert AvgIntensity().is_built()
