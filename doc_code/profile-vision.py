#%%
# Casting inspection
from PIL import Image
from pathlib import Path

DATA_PATH = Path("../raymon/tests/sample_data/castinginspection/ok_front/")
LIM = 150


def load_data(dpath, lim):
    files = dpath.glob("*.jpeg")
    images = []
    for n, fpath in enumerate(files):
        if n == lim:
            break
        img = Image.open(fpath)
        images.append(img)
    return images


loaded_data = load_data(dpath=DATA_PATH, lim=LIM)

from raymon import ModelProfile, InputComponent
from raymon.profiling.extractors.vision import Sharpness, DN2AnomalyScorer


profile = ModelProfile(
    name="casting-inspection",
    version="0.0.1",
    components=[
        InputComponent(name="sharpness", extractor=Sharpness()),
        InputComponent(name="outlierscore", extractor=DN2AnomalyScorer(k=16)),
    ],
)

profile.build(input=loaded_data)
#%%
profile.view()
#%%
tags = profile.validate_input(loaded_data[-1])
tags
#%%
profile.view(tags)

#%%
from PIL import ImageFilter

img_blur = loaded_data[-1].copy().filter(ImageFilter.GaussianBlur(radius=5))
img_blur
with open("blur.jpg", "wb") as f:
    img_blur.save(f)


#%%
tags_blur = profile.validate_input(img_blur)
tags_blur

#%%

profile.view(poi=tags_blur)


#%%
import pickle
from raymon.profiling.components import DataType
from raymon import ModelProfile, InputComponent, OutputComponent, ActualComponent, EvalComponent
from raymon.profiling.extractors.vision import YoloConfidenceExtractor, Sharpness
from raymon.profiling.scores import MeanScore

with open("/Users/kv/Raymon/Code/raymon/raymon/tests/sample_data/coco/input-output.pkl", "rb") as f:
    images, outputs = pickle.load(f)

yolo_profile = ModelProfile(
    name="Yolo",
    version="1.0.0",
    components=[
        InputComponent(name="sharpness", dtype=DataType.FLOAT, extractor=Sharpness()),
        OutputComponent(name="confidence", extractor=YoloConfidenceExtractor()),
    ],
    scores=[MeanScore(name="mean_confidence", inputs=["confidence"], preference="high")],
)

yolo_profile.build(input=images, output=outputs)
yolo_profile.view()
# %%

#%%
