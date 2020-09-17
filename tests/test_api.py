# %%
import base64
import json
from io import BytesIO

import numpy as np
import pytest
import requests
import yaml
from IPython.core.display import HTML, display
from PIL import Image

import raymon.types as rt


URL = 'http://localhost:8000'
PATH = "./manifest.yml"


@pytest.fixture()
def project_config():
    with open(PATH, 'r') as f:
        cfg = yaml.full_load(f)
    return cfg


def test_create_project(project_config):
    proj_name = "casting_inspection"
    resp = requests.post(f"{URL}/projects/{proj_name}",
                         params={},
                         json=project_config,
                         )
    assert resp.status_code == 201
    resp.json()

# # %%
# # List projects

# resp = requests.get(f"{URL}/project",
#                     params={},
#                     headers={'Content-type': 'application/json'})
# resp.json()
# #%%
# #Create a project

# #%%
# # Apply orchestration
# cfg = load_fresh()

# resp = requests.post(f"{URL}/orchestration",
#                      params={'project_id': PROJECT_NAME},
#                      json=cfg)
# resp.json()


# # %%
# # Get orchestration
# # Apply orchestration
# resp = requests.get(f"{URL}/orchestration",
#                     params={'project_id': PROJECT_NAME})
# resp.json()


# # %%
# resp = requests.get(f"{URL}/object",
#                     params={'object_id': 'aafdc7c5-413eae6-4722-809c-69da1cccd9d1'},
#                     headers={'Content-type': 'application/json'})
# print(f"Response {resp}")
# resp.json().keys()

# # %%
# imggs = rt.from_dict(resp.json())
# type(imggs)

# # %%


# def rtgray2pil(rt_img):
#     return Image.fromarray(np.uint8(rt_img.data*255), 'L')


# def rtrgb2pil(rt_img):
#     return Image.fromarray(rt_img.data)


# def img2html(pilimg):
#     buffer = BytesIO()
#     pilimg.save(buffer, format="png")
#     myimage = buffer.getvalue()
#     bytestr = b"data:image/png;base64,"+base64.b64encode(myimage)
#     srcstr = bytestr.decode('ascii')
#     htmlstr = f'<img src="{srcstr}" />'
#     return htmlstr


# htmlstr = img2html(rtgray2pil(imggs))
# display(HTML(htmlstr))

# # %%
# lenna = Image.open("./Lenna.png")
# rtlenna = rt.ImageRGB(np.array(lenna))
# Image.fromarray(rtlenna.data)
# htmlstr = img2html(rtrgb2pil(rtlenna))
# display(HTML(htmlstr))


# # %%
# # Call faas
# FAAS_BASE_URL = "http://localhost:8080/function/"

# payload = {
#     'func_params': {},
#     'data': rtlenna.to_jcr()
# }

# r = requests.post(FAAS_BASE_URL+"vis-img2html", json=payload)
# display(HTML(r.text))


# # %%
# lenna = Image.open("./Lenna.png")
# rtlenna = rt.ImageRGB(np.array(lenna))

# lennajson = rtlenna.to_json()
# restoredlenna = rt.from_dict(json.loads(lennajson))
# Image.fromarray(restoredlenna.data.astype(np.uint8))

# # %%
# restoredlenna


# # %%
