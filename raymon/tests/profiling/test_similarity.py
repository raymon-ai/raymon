from raymon.profiling.extractors.vision import FixedSubpatchSimilarity
from raymon.tests.conftest import images
import imagehash


def test_patch():
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64})
    extractor.patch = {"x0": 0, "y0": 0, "x1": 128, "y1": 64}
    assert extractor.patch["x1"] == 128
    extractor.patch = [0, 0, 64, 64]
    assert extractor.patch["x1"] == 64


def test_nrefs():
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=5)
    extractor.nrefs = 1
    assert extractor.nrefs == 1
    extractor.refs = ["adf8d224cb8786cc"]
    assert isinstance(extractor.refs, list)
    assert isinstance(extractor.refs[0], imagehash.ImageHash)


def test_idfr():
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, idfr="Emre")
    extractor.idfr = "Emre2"
    assert extractor.idfr == "Emre2"
    extractor.idfr = 2
    assert isinstance(extractor.idfr, str)


def test_extract(images):
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=3)
    extractor.build(images)
    assert isinstance(extractor.extract(images[0]), int)


def test_build(images):
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=2)
    extractor.build(images)
    assert len(extractor.refs) == 2
    assert isinstance(extractor.refs[0], imagehash.ImageHash)


def test_to_jcr(images):
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=2)
    extractor.build(images)
    jcr = extractor.to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.vision.similarity.FixedSubpatchSimilarity"
    assert jcr["state"]["patch"] == {"x0": 0, "y0": 0, "x1": 64, "y1": 64}
    assert jcr["state"]["nrefs"] == 2
    assert isinstance(jcr["state"]["refs"][0], str)


def test_from_jcr(images):
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=2)
    extractor.build(images)
    jcr = extractor.to_jcr()
    other_extractor = extractor.from_jcr(jcr["state"])
    assert isinstance(other_extractor, FixedSubpatchSimilarity)
    assert extractor.patch["x1"] == 64
    assert extractor.nrefs == 2
    assert len(extractor.refs) == 2
    assert isinstance(extractor.refs[0], imagehash.ImageHash)


def test_is_built(images):
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=2)
    extractor.build(images)
    assert extractor.is_built()


def test_str():
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=2)
    assert str(extractor) == "raymon.profiling.extractors.vision.similarity.FixedSubpatchSimilarity (None)"
