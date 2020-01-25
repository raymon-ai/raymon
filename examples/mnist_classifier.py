# based on https://github.com/pytorch/examples/tree/master/mnist
#%%
%load_ext autoreload
%autoreload 2

import argparse
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms

from raymon.external import APILogger
from raymon.ray import Ray
import raymon.types as rt

# ray = FileLogger(fpath='raymon.log', stdout=True, context="MNIST Example")
ray_api = APILogger(url="http://localhost:8000", context="MNIST Example", project_id="Testing")


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4*4*50, 500)
        self.fc2 = nn.Linear(500, 10)

    def forward(self, x, ray):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        ray.log(peephole='l1_features', data=rt.Numpy(np.squeeze(data.numpy(), 0)))
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        ray.log(peephole='l2_features', data=rt.Numpy(np.squeeze(data.numpy(), 0)))
        x = x.view(-1, 4*4*50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        final = F.log_softmax(x, dim=1)
        return final



def process_ray(model, ray, data, target):
    model.eval()
    with torch.no_grad():
        output = model(data, ray=ray)
        pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
        correct = pred.eq(target.view_as(pred)).sum().item()
        return correct

#%%
device = 'cpu'
test_loader = torch.utils.data.DataLoader(
    datasets.MNIST(root='/Users/kv/Downloads/raymon_data/mnist', 
                   train=False, 
                   download=True,
                   transform=transforms.Compose([
                        transforms.ToTensor(),
                        transforms.Normalize((0.1307,), (0.3081,))  # TODO: Wrap callable
                    ])),
    batch_size=1, 
    shuffle=True)

model = Net().to(device)
for i, (data, target) in enumerate(test_loader):
    ray = Ray(logger=ray_api)
    # ray.log_id(ray_id)  # Will make sure the ray is registered.
    ray.log(peephole="Ingestion", data=rt.Text("Received new ray"))
    ray.log(peephole='network_input_img',  data=rt.ImageGrayscale(np.squeeze(data.numpy())))

    data, target = data.to(device), target.to(device)
    correct = process_ray(model, ray=ray, data=data, target=target)
    if i == 0:
        break


# # %%
# data, target = next(iter(test_loader))
# rm_img = rt.ImageGrayscale(np.squeeze(data.numpy()))

# # %%
# from bokeh.plotting import figure, show, output_file, output_notebook
# from bokeh.embed import json_item
# # output_file()

# p = rm_img.visualize(json=False)
# show(p)
# # %%
# import raymon.transforms as tfs

# hist_tf = tfs.Histogram()
# hist = hist_tf(rm_img)

# # %%
# p = hist.visualize(json=False)
# show(p)

# # %%
# from PIL import Image
# rgb_img = np.array(Image.open('/Users/kv/stack/Startup/Raymon/Code/raymon/bunny.jpeg').resize((350, 500)))
# rm_rgb = rt.ImageRGBA(data=rgb_img)
# show(rm_rgb.visualize(json=False, plot_width=500, plot_height=350))

# # %%
