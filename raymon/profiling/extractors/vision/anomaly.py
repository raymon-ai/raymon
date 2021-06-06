import numpy as np
import torch
import base64
import torchvision.models as models
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image

from raymon.profiling.extractors.structured.kmeans import KMeansOutlierScorer

# Loosely based on "Deep Nearest Neighbor Anomaly Detection": https://arxiv.org/abs/2002.10445


class ImageDataset(Dataset):
    """Face Landmarks dataset."""

    def __init__(self, loaded_data, transform=None):

        self.loaded_data = loaded_data
        self.transform = transform

    def __len__(self):
        return len(self.loaded_data)

    def __getitem__(self, idx):
        sample = self.loaded_data[idx]
        if self.transform:
            sample = self.transform(sample)
        return sample


class DN2AnomalyScorer(KMeansOutlierScorer):
    def __init__(self, k=16, size=None, clusters=None, dist="euclidean"):
        super().__init__(k=k, clusters=clusters, dist=dist)
        self.mobilenet = models.mobilenet_v2(pretrained=True).eval()
        self.size = size
        tfs = [
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
        if size is not None:
            tfs.append(
                transforms.Resize(size=size),
            )
        self.tfs = transforms.Compose(tfs)

    def extract(self, data):
        if not isinstance(data, Image.Image):
            raise ValueError(f"data must be of type PIL.Image.Image, not {data.shape}")
        batchtf = self.tfs(data)[None, :]
        feats = self.mobilenet(batchtf).detach().numpy()
        return super().extract(data=feats)

    def build(self, data, batch_size=16):
        dataset = ImageDataset(loaded_data=data, transform=self.tfs)
        # data is a list of images here
        dataloader = DataLoader(dataset, shuffle=False, batch_size=batch_size, drop_last=True)
        embeddings = torch.zeros(size=(len(data), 1000))
        for batchidx, batchtf in enumerate(dataloader):
            # batchtf = self.tfs(batch)
            components = self.mobilenet(batchtf).detach()  # .numpy()
            startidx = batchidx * batch_size
            stopidx = startidx + len(components)
            embeddings[startidx:stopidx, :] = components

        embeddings = embeddings[embeddings.abs().sum(axis=1) != 0]
        embeddings = embeddings.numpy()
        super().build(data=embeddings)

    """Serializable interface"""

    def to_jcr(self):
        b64 = base64.b64encode(self.clusters).decode()
        diststr = [k for k, v in self.dist_choices.items() if v == self.dist][0]
        data = {"clusters": b64, "k": self.k, "dist": diststr, "size": self.size}
        state = {"class": self.class2str(), "state": data}
        return state

    @classmethod
    def from_jcr(cls, jcr):
        k = jcr["k"]
        b64 = jcr["clusters"]
        dist = jcr["dist"]
        size = jcr["size"]
        clusters = np.frombuffer(base64.decodebytes(b64.encode()), dtype=np.float64).reshape((k, -1))
        return cls(k=k, size=size, clusters=clusters, dist=dist)
