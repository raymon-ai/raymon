from raymon.profiling.extractors.vision import AvgIntensity
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
    extractor = AvgIntensity()
    assert isinstance(extractor.extract(test_data[0]), float)


def test_extract_multiple():
    extractor = AvgIntensity()
    avg_intensity_list = extractor.extract_multiple(test_data)
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


def test_build():
    extractor = AvgIntensity()
    extractor.build(test_data[0])


def test_is_built():
    extractor = AvgIntensity()
    assert extractor.is_built()
