import numpy as np
from PIL import Image
import math
import glob
from collections.abc import Iterable
from raymon.profiling.extractors.vision import DN2AnomalyScorer
from PIL import ImageFilter


def test_preprocess(images):
    extractor = DN2AnomalyScorer(k=3)
    pil_image = images[0]
    numpy_img = np.array(pil_image)
    img_list = [pil_image, numpy_img]
    for img in img_list:
        actual_image = extractor.preprocess(img)
        assert isinstance(actual_image, np.ndarray)
        assert actual_image.shape == (3, 224, 224)


def test_batcher_normal(images):
    extractor = DN2AnomalyScorer(k=3)
    batch_size = 5
    batch_iterator = extractor.batches(images, batch_size)
    batch = next(iter(batch_iterator))
    assert len(batch) == 5


def test_build(images):
    extractor = DN2AnomalyScorer(k=3)
    extractor.build(data=images, batch_size=5)
    actual_cluster_number = len(extractor.clusters)
    expected_cluster_number = extractor.k
    message = f"Build method fails because amount of the cluster must equal k value {extractor.k} of DN2AnomalyScorer, but {actual_cluster_number}"
    assert actual_cluster_number == expected_cluster_number, message


def test_extract(images):
    extractor = DN2AnomalyScorer(k=3)
    extractor.build(data=images, batch_size=5)
    normal_image_path = "raymon/tests/sample_data/retinopathy/863_right.jpeg"
    normal_image = Image.open(normal_image_path)
    normal_image.thumbnail(size=(500, 500))
    normal_outlier_score = extractor.extract(normal_image)
    blur_image = normal_image.copy().filter(ImageFilter.GaussianBlur(radius=3))
    blur_image.thumbnail(size=(500, 500))
    blur_outlier_score = extractor.extract(blur_image)
    message = "Blurred image's outlier score must be bigger than normal image's everytime."
    assert isinstance(normal_outlier_score, float)
    assert blur_outlier_score > normal_outlier_score, message


def test_to_jcr(images):
    extractor = DN2AnomalyScorer(k=3)
    extractor.build(data=images, batch_size=5)
    assert extractor.to_jcr()["class"] == "raymon.profiling.extractors.vision.anomaly.DN2AnomalyScorer"
    assert extractor.to_jcr()["state"]["k"] == extractor.k


def test_from_jcr(images):
    extractor = DN2AnomalyScorer(k=3)
    extractor.build(data=images, batch_size=5)
    jcr = extractor.to_jcr()
    other_extractor = extractor.from_jcr(jcr["state"])
    assert other_extractor.k == extractor.k
    assert other_extractor.size == extractor.size
