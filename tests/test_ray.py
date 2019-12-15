#%%
from raymon.ray import Ray
from raymon.external import MockLogger


def test_split():
    logger = MockLogger()
    base_ray = Ray(logger=logger, ray_id="base")
    child = base_ray.split(suffix='a')
    assert child.ray_id == ("base", 'a')

def test_split_tuple():
    logger = MockLogger()
    base_ray = Ray(logger=logger, ray_id=('base', 'split'))
    child = base_ray.split(suffix='a')
    assert child.ray_id == ("base", 'split', 'a')
    
    
def test_merge():
    logger = MockLogger()
    base_ray = Ray(logger=logger, ray_id="base")
    children = [base_ray.split(suffix=str(i)) for i in range(10)]
    
    for child in children:
        assert len(child.ray_id) == 2
    merged_a = Ray.merge(raylist=children[:5], suffix="head")
    merged_b = Ray.merge(raylist=children[:5], suffix="tail")
    
    for i, pred in enumerate(merged_a.pred):
        pred == children[i]
    
    for i, pred in enumerate(merged_b.pred):
        pred == children[5+i]
        
    
test_merge()
