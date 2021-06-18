#%%Import Libraries 
import numpy as np
import random
from PIL import Image
from PIL import ImageFile
import math

from pathlib import Path
from raymon.profiling import (
    ModelProfile,
    InputComponent,
    DataType,
)
from raymon.profiling.extractors.vision import DN2AnomalyScorer

from PIL import ImageFilter
from PIL import ImageEnhance

#%%
ImageFile.LOAD_TRUNCATED_IMAGES = True
ROOT = Path("..").resolve()
DATA_PATH = ROOT / "profiling/retinopathy_data/1"
# Bilding Data contains max 500 different images
LIM = 500

def load_data(dpath, lim):
    files = dpath.glob("*.jpeg")
    images = []
    for n, fpath in enumerate(files):
        if n == lim:
            break
        img = Image.open(fpath)
        img.thumbnail(size=(500, 500))
        images.append(img)
    return images

profile = ModelProfile(
    name="retinopathy",
    version="2.0.0",
    components=[
        InputComponent(
            name="outlierscore",
            extractor=DN2AnomalyScorer(k=20, size=(256, 256)),
            dtype=DataType.FLOAT,
        )
    ]
)
loaded_data = load_data(DATA_PATH, lim=LIM)
profile.build(input=loaded_data)

def test_build_model():
    actual_extractor_type = type(profile.components['outlierscore'].extractor)
    expected_extractor_type = DN2AnomalyScorer
    message = f"Type of extractor have to be DN2AnomalyScorer, but {actual_extractor_type}"
    assert actual_extractor_type==expected_extractor_type, message

def test_prepare_batch():
    loaded_data = load_data(DATA_PATH, lim=LIM) 
    batch_size=10
    actual_batch_number = len(profile.components['outlierscore'].extractor.prepare_batch(loaded_data, batch_size))
    expected_batch_number = math.ceil(len(loaded_data)/batch_size)
    message = "batch number have to equal -the number of images / batch size (round up) -"
    assert  actual_batch_number == expected_batch_number, message

def test_cluster_amount():   
    profile = test_build_model()
    actual_cluster_number = len(profile.components['outlierscore'].extractor.clusters)
    expected_cluster_number = profile.components['outlierscore'].extractor.k
    message = f'Building model fails because cluster have to equal k value of DN2AnomalyScorer, but {actual_cluster_number}'
    assert actual_cluster_number == expected_cluster_number, message

def test_outlier_score():
    TEST_DATA_PATH = ROOT / "profiling/retinopathy_data/3"
    # Test data contains max 10 different images
    test_LIM = 10
    test_data = load_data(dpath=TEST_DATA_PATH, lim=test_LIM)

    # Test normal images' outlier score vs blurred images' outlier score
    for img in test_data:
        tags = profile.validate_input(img)
        # Make each image blurred
        img_blur = img.copy().filter(ImageFilter.GaussianBlur(radius=3))
        tags_blur = profile.validate_input(img_blur)
        message = "Blurred image's value have to be bigger than normal image everytime."
        assert int(tags[0]['value']) < int(tags_blur[0]['value']), message



# Can we support any iterable? -> THIS IS A TEST
# Let's try to support numpy arrays too. -> THIS IS A TEST
# compare two certain images normal vs blur
# test the building of the extractor
# test the amount of clusters
# test whether the extractor can be serialized correctly and loaded correctly etc.
