# based on https://github.com/pytorch/examples/tree/master/mnist
#%%
import raymon.types as rt
from raymon.ray import Ray
from raymon.loggers import RaymonAPI

from torchvision import datasets, transforms
import torch.optim as optim
import torch.nn.functional as F
import torch.nn as nn
import torch
import numpy as np
from pathlib import Path
import argparse
from raymon.loggers import RaymonAPI

torch.set_grad_enabled(False)

#%%
class OutsideWorld:
    def __init__(self):
        self.test_loader = iter(
            torch.utils.data.DataLoader(
                datasets.MNIST(
                    root="/Users/kv/Downloads/raymon_data/mnist",
                    train=False,
                    download=True,
                    transform=transforms.Compose(
                        [
                            transforms.ToTensor(),
                            # transforms.Normalize((0.1307,), (0.3081,))  # TODO: Wrap callable
                        ]
                    ),
                ),
                batch_size=1,
                shuffle=True,
            )
        )

    def send_data(self):
        data, target = next(self.test_loader)
        data, target = data.to("cpu"), target.to("cpu")
        return data


#%%


class MLModel(nn.Module):
    def __init__(self):
        super(MLModel, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4 * 4 * 50, 500)
        self.fc2 = nn.Linear(500, 10)

    def forward(self, x, ray):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        # ray.log(peephole='l1_features', data=rt.Numpy(np.squeeze(data.numpy(), 0)))
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        # ray.log(peephole='l2_features', data=rt.Numpy(np.squeeze(data.numpy(), 0)))
        x = x.view(-1, 4 * 4 * 50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        final = F.log_softmax(x, dim=1)
        return final


class Deployment:
    def __init__(self, model):
        self.model = model
        self.model.eval()
        # Specify the Raymon API endpoint
        self.raymon = RaymonAPI(url="http://localhost:8000", context="QA Deployment", project_id="casting_inspection")

    def process(self, data):
        # Every time you want to trace some data through your system, Do so by creating a
        # Ray object
        ray = Ray(logger=self.raymon)
        # At any time, you can log data to the backend using the ray object
        # ray.metadata({
        #     'machine': 'casting_5'
        # })
        ray.log(peephole="network_input_img", data=rt.ImageGrayscale(np.squeeze(data.numpy())))

        # You can pass it on to other places...
        output = self.model(data, ray=ray)
        return output


def test_post():
    world = OutsideWorld()
    deployment = Deployment(model=MLModel().to("cpu"))
    for _ in range(10):
        data = world.send_data()
        deployment.process(data)


if __name__ == "__main__":
    test_post()
