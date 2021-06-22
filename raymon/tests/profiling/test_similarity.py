from raymon.profiling.extractors.vision import FixedSubpatchSimilarity
import glob
from PIL import Image
import imagehash


def load_data(dpath, lim):
    files = glob.glob(dpath + "/*.jpeg")
    images = []
    for n, fpath in enumerate(files):
        if n == lim:
            break
        img = Image.open(fpath)
        img.thumbnail(size=(500, 500))
        images.append(img)
    return images


test_LIM = 10
test_data = load_data(dpath="raymon/tests/sample_data", lim=test_LIM)


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


def test_extract():
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=3)
    extractor.build(test_data)
    assert isinstance(extractor.extract(test_data[0]), int)


def test_build():
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=2)
    extractor.build(test_data)
    assert len(extractor.refs) == 2
    assert isinstance(extractor.refs[0], imagehash.ImageHash)


def test_to_jcr():
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=2)
    extractor.build(test_data)
    jcr = extractor.to_jcr()
    assert jcr["class"] == "raymon.profiling.extractors.vision.similarity.FixedSubpatchSimilarity"
    assert jcr["state"]["patch"] == {"x0": 0, "y0": 0, "x1": 64, "y1": 64}
    assert jcr["state"]["nrefs"] == 2
    assert isinstance(jcr["state"]["refs"][0], str)


def test_from_jcr():
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=2)
    extractor.build(test_data)
    jcr = extractor.to_jcr()
    isinstance(extractor.from_jcr(jcr), FixedSubpatchSimilarity)


def test_is_built():
    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, nrefs=2)
    extractor.build(test_data)
    assert extractor.is_built()
