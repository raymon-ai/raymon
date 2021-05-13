import pytest
import json
from raymon import ModelProfile
from raymon import FloatComponent
from raymon import NumericStats, CategoricStats
from raymon.profiling.extractors.vision.similarity import FixedSubpatchSimilarity


def test_stats_none():
    stats = NumericStats()
    jcr = stats.to_jcr()
    for attr in NumericStats._attrs:
        assert jcr[attr] is None


def test_stats_partial_none():
    params = dict(min=0, max=1, mean=0.5, std=0.02, pinv=0.1, percentiles=list(range(101)), samplesize=10)
    stats = NumericStats(**params)
    jcr = stats.to_jcr()
    for attr in NumericStats._attrs:
        assert jcr[attr] == params[attr]


def test_num_stats_build():
    stats = NumericStats()
    assert not stats.is_built()
    stats = NumericStats(
        min=0,
        max=1,
        mean=0.5,
        std=0.02,
    )
    assert not stats.is_built()
    stats = NumericStats(min=0, max=1, mean=0.5, percentiles=range(101), pinv=0)
    assert not stats.is_built()
    stats = NumericStats(min=0, max=1, std=0.02, percentiles=range(101), pinv=0)
    assert not stats.is_built()
    stats = NumericStats(min=0, mean=0.5, std=0.02, percentiles=range(101), pinv=0)
    assert not stats.is_built()
    stats = NumericStats(max=1, mean=0.5, std=0.02, percentiles=range(101), pinv=0)
    assert not stats.is_built()
    stats = NumericStats(min=0, max=1, mean=0.5, std=0.02, percentiles=range(101))
    assert not stats.is_built()
    stats = NumericStats(min=0, max=1, mean=0.5, std=0.02, percentiles=range(101), pinv=0, samplesize=10)
    assert stats.is_built()


def test_cat_stats_build():
    stats = CategoricStats()
    assert not stats.is_built()
    stats = CategoricStats(frequencies={"a": 0.5, "b": 0.5}, pinv=0.1)
    assert not stats.is_built()
    stats = CategoricStats(frequencies={"a": 0.5, "b": 0.5}, samplesize=10)
    assert not stats.is_built()
    stats = CategoricStats(pinv=0.1, samplesize=10)
    assert not stats.is_built()
    stats = CategoricStats(frequencies={"a": 0.5, "b": 0.5}, pinv=0.1, samplesize=10)
    assert stats.is_built()


def test_subpatchsimilarity_extractor_buildable():
    with pytest.raises(ValueError):
        extractor = FixedSubpatchSimilarity(patch=None)

    extractor = FixedSubpatchSimilarity(patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64})
    assert not extractor.is_built()

    extractor = FixedSubpatchSimilarity(
        patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, refs=["adf8d224cb8786cc"], nrefs=1
    )
    assert extractor.is_built()


def test_component_buildable():
    extractor = FixedSubpatchSimilarity(
        patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, refs=["adf8d224cb8786cc"], nrefs=1
    )
    stats = NumericStats(min=0, max=1)
    component = FloatComponent(name="testcomponent", extractor=extractor, stats=stats)
    assert not stats.is_built()
    assert extractor.is_built()
    assert not component.is_built()

    extractor = FixedSubpatchSimilarity(
        patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, refs=["adf8d224cb8786cc"], nrefs=1
    )
    stats = NumericStats(min=0, max=1, mean=0.5, std=0.02, percentiles=range(101), pinv=0, samplesize=10)
    component = FloatComponent(name="testcomponent", extractor=extractor, stats=stats)
    assert stats.is_built()
    assert extractor.is_built()
    assert component.is_built()


def test_schema_buildable():
    extractor = FixedSubpatchSimilarity(
        patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, refs=["adf8d224cb8786cc"], nrefs=1
    )
    stats = NumericStats(min=0, max=1)
    component = FloatComponent(name="testcomponent", extractor=extractor, stats=stats)
    schema = ModelProfile(name="Testing", version="1.0.0", input_comps=[component])

    assert not schema.is_built()

    extractor = FixedSubpatchSimilarity(
        patch={"x0": 0, "y0": 0, "x1": 64, "y1": 64}, refs=["adf8d224cb8786cc"], nrefs=1
    )
    stats = NumericStats(min=0, max=1, mean=0.5, std=0.02, percentiles=range(101), pinv=0, samplesize=10)
    component = FloatComponent(name="testcomponent", extractor=extractor, stats=stats)
    schema = ModelProfile(name="Testing", version="1.0.0", input_comps=[component, component])

    assert schema.is_built()
