#%%
import json
import click
import yaml
import requests
import msgpack
from raymon.external import RaymonAPI

viz_obj_id = '63504979-3819-4ba5-afb6-829d0bb36c1f'

api = RaymonAPI(url="http://localhost:8000")
api.login()
params = {'object_id': viz_obj_id}
resp = api.get(route=f'object', params=params).json()

#%%
bokeh = resp['object']['data']
# # %%
# data = {
#     'hello': 'world'
# }


# # %%
# import base64
# in_string = base64.b64encode(msgpack.packb(data)).decode('ascii')
# in_string

# msgpack.unpackb(base64.b64decode(in_string.encode('ascii')), raw=False)


# # %%
# def decode(ascii_str):
    
#     return msgpack.unpackb(base64.b64decode(ascii_str.encode('ascii')), raw=False)
    

# decoded = decode(resp['object'])
# # %%
# decoded.keys()
# # %%
# decoded['type']
# # decoded['data']

# # %%


# %%
bokeh['doc'].keys()


# %%
bokeh['doc']['roots'].keys()

# %%
