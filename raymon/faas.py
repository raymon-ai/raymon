#%%
import json
from functools import partial

import raymon.types as rt

def handle_builder(func):

    def handle(req, func):
        req_loaded = json.loads(req)            
        func_params = req_loaded["func_params"]
        if isinstance(req_loaded, list):
            rdata = [rt.from_json(inst) for inst in req_loaded["data"]]
        else:
            rdata = rt.from_json(req_loaded["data"])
        result = func(rdata, **func_params)
        return result.to_json()
    
    return partial(handle, func=func)


# %%
