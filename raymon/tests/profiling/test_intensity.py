from raymon.profiling.extractors.vision import AvgIntensity
from raymon.tests.conftest import load_data


def test_extract(load_data):
    extractor = AvgIntensity()
    assert isinstance(extractor.extract(load_data[0]), float)


def test_extract_multiple(load_data):
    extractor = AvgIntensity()
    avg_intensity_list = extractor.extract_multiple(load_data)
    assert isinstance(avg_intensity_list, list)
    assert isinstance(avg_intensity_list[0], float)


def test_to_jcr():
    extractor = AvgIntensity()
    jcr = extractor.to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.vision.intensity.AvgIntensity"
    assert len(jcr["state"]) == 0


def test_from_jcr():
    extractor = AvgIntensity()
    jcr = extractor.to_jcr()
    assert isinstance(extractor.from_jcr(jcr), AvgIntensity)


def test_build(load_data):
    extractor = AvgIntensity()
    extractor.build(load_data[0])


def test_is_built():
    extractor = AvgIntensity()
    assert extractor.is_built()
