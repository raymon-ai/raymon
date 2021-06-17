#%%Import Libraries 
import numpy as np
import random
from PIL import Image
from PIL import ImageFile

from pathlib import Path
from raymon.profiling import (
    ModelProfile,
    InputComponent,
    DataType,
)
from raymon.profiling.extractors.vision import DN2AnomalyScorer

from PIL import ImageFilter
from PIL import ImageEnhance

def test_DN2AnomalyScorer():
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    ROOT = Path("..").resolve()
    # test data contains 11 different images
    TEST_DATA_PATH = ROOT / "profiling/retinopathy_data/3"
    LIM = 500
    
    def load_data(dpath, lim):
        files = dpath.glob("*.jpeg")
        images = []
        metadata = []
        for n, fpath in enumerate(files):
            if n == lim:
                break
            img = Image.open(fpath)
            img.thumbnail(size=(500, 500))
            images.append(img)
            metadata.append([{"name": "srcfile", "value": fpath.stem, "type": "label"}])
        return images, metadata

    # Load model, you can see how the model build.
    MODEL_PATH = ROOT / "profiling/models/retinopathy@2.0.0.json"
    profile = ModelProfile().load(MODEL_PATH)

    test_data, metadata = load_data(dpath=TEST_DATA_PATH, lim=LIM)

    for img in test_data:
        tags = profile.validate_input(img)
        # I made each image blurred
        img_blur = img.copy().filter(ImageFilter.GaussianBlur(radius=3))
        tags_blur = profile.validate_input(img_blur)
        # blurred image's value have to be bigger than normal image everytime.
        assert int(tags[0]['value']) < int(tags_blur[0]['value'])


##### I build a model with 500 images and with my DN2AnomalyScorer class
##### Create Profile class
#profile = ModelProfile(
#    name="retinopathy",
#    version="2.0.0",
#    components=[
#        InputComponent(
#            name="outlierscore",
#            extractor=DN2AnomalyScorer(k=20, size=(256, 256)),
#            dtype=DataType.FLOAT,
#        )
#    ]
#)
###### Save the model
# profile.build(input=loaded_data)
# fullprofile_path = Path("models/")
# profile.save(fullprofile_path)

