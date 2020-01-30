#%%
from bokeh.palettes import Plasma256
import numpy as np
import random
import bokeh
from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.embed import components

import pandas as pd
# output_notebook()

# %%
hist_bins = np.arange(32)
hist_bins
# %%
n_buckets = 32
n_times = 50
temp_bins = np.ones((n_buckets, n_times))
abs_counts = np.ones((n_buckets, n_times))

for t in range(n_times):
    bins = np.zeros(n_buckets)

    if t < 30:
        idx = 0
    else:
        idx = int((t-30)// 5)
    bins[idx] = 480
    bins[-1] = 120
    bins += np.random.randint(low=1, high=60, size=n_buckets)
    abs_counts[:, t] = bins
    bins = bins / bins.sum()
    temp_bins[:, t] = bins
    

dict_data = []
for ts in range(n_times):
    for bn in range(n_buckets):
        dict_data.append({
            'ts': ts,
            'bin_number': bn,
            'count': abs_counts[bn, ts],
            'alpha': temp_bins[bn, ts],
            'plasma': Plasma256[int(temp_bins[bn, ts] * 255)]
        })
df = pd.DataFrame(dict_data)
df
p = figure(title="Evolution of histograms over time",
           tools="hover,save,wheel_zoom",
        #    x_range=range(n_times), y_range=range(n_buckets),
           tooltips=[('(ts, bin_number)', '@ts, @bin_number'), ('count', '@count')])

p.plot_width = 1200
p.plot_height = 400
p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
# p.axis.major_label_text_font_size = "5pt"
p.xaxis.axis_label = 'Time bucket'
p.yaxis.axis_label = 'Bucket count'

p.axis.major_label_standoff = 0
color = 'orange' # 'plasma'  # 'orange'
alpha = 'alpha' # 1  # 'alpha'
p.rect('ts', 'bin_number', 0.9, 0.9, source=df,
    color=color, alpha=alpha, line_color=None,
    hover_line_color='black', hover_color=color)


show(p)  # show the plot


# %%

script, div = components(p, wrap_script=False)
vue_plot = {
    'bokehVersion': bokeh.__version__,
    'div': [div], 
    'script': [script]
    }
data = {
    'type': 'bokeh',
    'data': vue_plot
}
# %%
import json
with open("/Users/kv/stack/Startup/Raymon/Code/plot.json", 'w') as f:
    json.dump(vue_plot, f)
# %%
