#%%
import json
from functools import partial

import raymon.types as rt

def handle_builder(func):

    def handle(req, func):
        req_json = json.loads(req)
        func_params = req_json["func_params"]
        rdata = rt.from_json(req_json["data"])
        result = func(rdata, **func_params)
        return result.to_json()
    return partial(handle, func=func)


# %%
