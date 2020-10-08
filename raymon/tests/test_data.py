#%%
from raymon import types as rt
import pandas as pd
from pathlib import Path
import json


def test_df_save_load(tmp_path):
    tmp_file = tmp_path / 'df.json'
    cols = {'num1': list(range(10)),
            'cat1': ['a'] * 5 + ['b'] * 5,
            'cat2': ['c'] * 5 + ['d'] * 5,
            'num2': list(range(0, 20, 2))}
    df = pd.DataFrame(data=cols)
    
    rdf = rt.DataFrame(data=df)
    df_jcr = rdf.to_jcr()
    with open(tmp_file, 'w') as f:
        json.dump(df_jcr, f)
        
    with open(tmp_file, 'r') as f:
        jcr_rest = json.load(f)
    
    df_rest = rt.load_jcr(jcr_rest)
    assert (rdf.data == df_rest.data).all().all()
    
    

# %%
