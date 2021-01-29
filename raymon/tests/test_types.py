#%%
import pytest
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from PIL import ImageChops

from raymon import types as rt


"""Basic tests"""


def test_laod_abc():
    with pytest.raises(TypeError):
        rdf = rt.RaymonDataType()


"""Image tests"""


def test_image_invalid():
    with pytest.raises(ValueError):
        rdf = rt.DataFrame(data=None)


def test_image_lossless():
    img = Image.open(Path(__file__).parents[0] / "Lenna.png")
    rimg = rt.Image(img, lossless=True)
    jcr = rimg.to_jcr()

    rimg_rest = rt.load_jcr(jcr)
    diff = ImageChops.difference(rimg.data, rimg_rest.data)
    assert not diff.getbbox()


def test_image_lossy():
    img = Image.open(Path(__file__).parents[0] / "Lenna.png")
    rimg = rt.Image(img)
    jcr = rimg.to_jcr()

    rimg_rest = rt.load_jcr(jcr)
    diff = ImageChops.difference(rimg.data, rimg_rest.data)
    # This may have differences
    assert diff.getbbox()


"""Numpy tests"""


def test_np_invalid():
    # tmp_file = tmp_path / 'df.json'

    arr = [1, 2, 3, 4]
    with pytest.raises(ValueError):
        rdf = rt.Numpy(data=arr)


def test_np_save_load():
    # tmp_file = tmp_path / 'df.json'
    arr = np.array([[1, 2, 3, 4], [1, 2, 3, 4], [10, 20, 30, 40]])

    wrapped = rt.Numpy(data=arr)
    wrapped_jcr = wrapped.to_jcr()

    wrapped_restored = rt.load_jcr(wrapped_jcr)
    assert (wrapped.data == wrapped_restored.data).all().all()


"""Pandas tests"""


def test_series_invalid():
    # tmp_file = tmp_path / 'df.json'

    df = np.array([1, 2, 3, 4])
    with pytest.raises(ValueError):
        rdf = rt.Series(data=df)


def test_series_save_load():
    # tmp_file = tmp_path / 'df.json'
    series = pd.Series([1, 2, 3, 4])

    rseries = rt.Series(data=series)
    series_jcr = rseries.to_jcr()

    series_restored = rt.load_jcr(series_jcr)
    assert (rseries.data.values == series_restored.data.values).all()


def test_df_invalid():
    # tmp_file = tmp_path / 'df.json'

    df = pd.Series([1, 2, 3, 4])
    with pytest.raises(ValueError):
        rdf = rt.DataFrame(data=df)


def test_df_save_load():
    # tmp_file = tmp_path / 'df.json'
    cols = {
        "num1": list(range(10)),
        "cat1": ["a"] * 5 + ["b"] * 5,
        "cat2": ["c"] * 5 + ["d"] * 5,
        "num2": list(range(0, 20, 2)),
    }
    df = pd.DataFrame(data=cols)

    rdf = rt.DataFrame(data=df)
    df_jcr = rdf.to_jcr()

    df_restored = rt.load_jcr(df_jcr)
    assert (rdf.data == df_restored.data).all().all()


# %%
"""Native tests"""


def test_jcr_invalid():
    # tmp_file = tmp_path / 'df.json'

    arr = np.array([1, 2, 3, 4])
    with pytest.raises(ValueError):
        rdf = rt.Native(data=arr)


def test_jcr_save_load_0():
    # tmp_file = tmp_path / 'df.json'
    jcr = [{"all": "this"}, {"is": "json dompable", 1: 10}]

    wrapped = rt.Native(data=jcr)
    wrapped_jcr = wrapped.to_jcr()

    wrapped_restored = rt.load_jcr(wrapped_jcr)
    for ela, elb in zip(wrapped.data, wrapped_restored.data):
        for key in set(list(ela.keys()) + list(elb.keys())):
            assert ela[key] == elb[key]


def test_jcr_save_load_1():
    # tmp_file = tmp_path / 'df.json'
    jcr = 1.01

    wrapped = rt.Native(data=jcr)
    wrapped_jcr = wrapped.to_jcr()

    wrapped_restored = rt.load_jcr(wrapped_jcr)
    assert wrapped.data == wrapped_restored.data


def test_jcr_save_load_2():
    # tmp_file = tmp_path / 'df.json'
    jcr = "This is a string"

    wrapped = rt.Native(data=jcr)
    wrapped_jcr = wrapped.to_jcr()

    wrapped_restored = rt.load_jcr(wrapped_jcr)
    assert wrapped.data == wrapped_restored.data
