from raymon.profiling.extractors.vision import Sharpness


def test_extract(images):
    assert isinstance(Sharpness().extract(images[0]), float)


def test_extract_multiple(images):
    avg_intensity_list = Sharpness().extract_multiple(images)
    assert isinstance(avg_intensity_list, list)
    assert isinstance(avg_intensity_list[0], float)


def test_to_jcr():
    jcr = Sharpness().to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.vision.sharpness.Sharpness"
    assert not jcr["state"]


def test_from_jcr():
    extractor = Sharpness()
    jcr = extractor.to_jcr()
    assert isinstance(extractor.from_jcr(jcr["state"]), Sharpness)


def test_build(images):
    assert not Sharpness().build(images[0])


def test_is_built():
    assert Sharpness().is_built()
