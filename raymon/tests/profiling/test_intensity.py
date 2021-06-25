from raymon.profiling.extractors.vision import AvgIntensity


def test_extract(images):
    assert isinstance(AvgIntensity().extract(images[0]), float)


def test_extract_multiple(images):
    avg_intensity_list = AvgIntensity().extract_multiple(images)
    assert isinstance(avg_intensity_list, list)
    assert isinstance(avg_intensity_list[0], float)


def test_to_jcr():
    jcr = AvgIntensity().to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.vision.intensity.AvgIntensity"
    assert len(jcr["state"]) == 0


def test_from_jcr():
    extractor = AvgIntensity()
    jcr = extractor.to_jcr()
    assert isinstance(extractor.from_jcr(jcr["state"]), AvgIntensity)


def test_build(images):
    AvgIntensity().build(images[0])


def test_is_built():
    assert AvgIntensity().is_built()
