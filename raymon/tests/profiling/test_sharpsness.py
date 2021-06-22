from raymon.profiling.extractors.vision import Sharpness
import glob
from PIL import Image


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


def test_extract():
    extractor = Sharpness()
    assert isinstance(extractor.extract(test_data[0]), float)


def test_extract_multiple():
    extractor = Sharpness()
    avg_intensity_list = extractor.extract_multiple(test_data)
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


def test_build():
    extractor = Sharpness()
    assert not extractor.build(test_data[0])


def test_is_built():
    extractor = Sharpness()
    assert extractor.is_built()
