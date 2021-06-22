import numpy as np
from PIL import Image
import math
import os
import glob
from collections.abc import Iterable
from raymon.profiling.extractors.vision import DN2AnomalyScorer


def load_data(dpath, lim):
    print(dpath)
    files = glob.glob(dpath + "/*.jpeg")
    print(os.getcwd())
    images = []
    for n, fpath in enumerate(files):
        if n == lim:
            break
        img = Image.open(fpath)
        img.thumbnail(size=(500, 500))
        images.append(img)
    return images


def test_preprocess():
    extractor = DN2AnomalyScorer(k=3, size=(256, 256))
    test_LIM = 10
    test_data = load_data(dpath="raymon/tests/sample_data", lim=test_LIM)
    pil_image = test_data[0]
    numpy_img = np.array(pil_image, dtype=np.float32)
    img_list = [pil_image, numpy_img]
    for img in img_list:
        actual_image = extractor.preprocess(img)
        assert isinstance(actual_image, np.ndarray)
        assert actual_image.shape == (1, 3, 224, 224)


def test_prepare_batch():
    extractor = DN2AnomalyScorer(k=3, size=(256, 256))
    test_LIM = 10
    test_data = load_data(dpath="raymon/tests/sample_data", lim=test_LIM)
    batch_size = 5
    actual_batch_number = len(extractor.prepare_batch(test_data, batch_size))
    expected_batch_number = math.ceil(len(test_data) / batch_size)
    message = "Batch number must equal -the number of images / batch size (round up) -"
    assert len(test_data) > 0
    assert isinstance(test_data, Iterable)
    assert actual_batch_number == expected_batch_number, message


def test_build():
    extractor = DN2AnomalyScorer(k=3, size=(256, 256))
    test_LIM = 10
    test_data = load_data(dpath="raymon/tests/sample_data", lim=test_LIM)
    extractor.build(data=test_data, batch_size=5)
    actual_cluster_number = len(extractor.clusters)
    expected_cluster_number = extractor.k
    message = f"Build method fails because amount of the cluster must equal k value {extractor.k} of DN2AnomalyScorer, but {actual_cluster_number}"
    assert actual_cluster_number == expected_cluster_number, message


def test_extract():
    extractor = DN2AnomalyScorer(k=3, size=(256, 256))
    test_LIM = 10
    test_data = load_data(dpath="raymon/tests/sample_data", lim=test_LIM)
    extractor.build(data=test_data, batch_size=5)
    normal_image_path = "raymon/tests/sample_data/863_right.jpeg"
    normal_image = Image.open(normal_image_path)
    normal_image.thumbnail(size=(500, 500))
    normal_outlier_score = extractor.extract(normal_image)
    blur_image_path = "raymon/tests/sample_data/8631_left.jpeg"
    blur_image = Image.open(blur_image_path)
    blur_image.thumbnail(size=(500, 500))
    blur_outlier_score = extractor.extract(blur_image)
    message = "Blurred image's outlier score must be bigger than normal image's everytime."
    assert isinstance(normal_outlier_score, float)
    assert blur_outlier_score > normal_outlier_score, message


def test_to_jcr():
    extractor = DN2AnomalyScorer(k=3, size=(256, 256))
    test_LIM = 10
    test_data = load_data(dpath="raymon/tests/sample_data", lim=test_LIM)
    extractor.build(data=test_data, batch_size=5)
    assert extractor.to_jcr()["class"] == "raymon.profiling.extractors.vision.anomaly.DN2AnomalyScorer"
    assert extractor.to_jcr()["state"]["k"] == extractor.k
    assert extractor.to_jcr()["state"]["size"] == extractor.size


def test_from_jcr():
    extractor = DN2AnomalyScorer(k=3, size=(256, 256))
    test_LIM = 10
    test_data = load_data(dpath="raymon/tests/sample_data", lim=test_LIM)
    extractor.build(data=test_data, batch_size=5)
    jcr = extractor.to_jcr()["state"]
    other_extractor = extractor.from_jcr(jcr)
    assert other_extractor.k == extractor.k
    assert other_extractor.size == extractor.size
