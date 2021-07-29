from features import WeatherSubExtractor

import glob
import pandas as pd
from PIL import Image
import json
import os
import pickle
import pkg_resources


class MetaExtractors:
    def __init__(self):
        self.class_name_dict = {}
        self.is_built = None
        self.paths = None

    def load(self):
        self.glare = self.load_model("glare")
        self.night = self.load_model("night")
        self.city = self.load_model("city")
        self.precipitation = self.load_model("precipitation")
        self.classname()

    def load_model(self, partname):
        sub_extractor = WeatherSubExtractor()
        if not pkg_resources.resource_filename("raymon", "models/weather/" + partname + ".sav"):
            print("There is no saved model, please build your model with your data for this " + partname + " part")
        else:
            self.svm_model = pickle.load(
                open(pkg_resources.resource_filename("raymon", "models/weather/" + partname + ".sav"), "rb")
            )
        return sub_extractor

    def build(self, paths):
        self.paths = paths
        self.glare = self.build_model("glare")
        self.night = self.build_model("night")
        self.city = self.build_model("city")
        self.precipitation = self.build_model("precipitation")
        self.is_built = True
        self.classname()

    def build_model(self, partname):
        data = self.load_data_clasification(self.paths[partname])
        sub_extractor = WeatherSubExtractor()
        sub_extractor.build(partname, data)
        self.class_name_dict[partname] = {str(i): name for i, name in enumerate(data.class_name.unique())}
        return sub_extractor

    def load_data_clasification(self, path, lim=300):
        images = []
        extensions = [".jpg", "jpeg", ".png", "webp"]
        for images_path, class_number in path.items():
            class_name = images_path.split("/")[-1]
            files = [x for x in glob.glob(images_path + "/*") if x.lower()[-4:] in extensions]
            for n, fpath in enumerate(files):
                if n == lim:
                    break
                img = Image.open(fpath)
                img.thumbnail(size=(500, 500))
                images.append((img, class_number, class_name))
        images_df = pd.DataFrame(images, columns=["images", "labels", "class_name"])
        return images_df

    def extract(self, image):
        features = self.glare.features(image)
        glare = self.glare.extract(features, self.class_name_dict["glare"])
        night = self.night.extract(features, self.class_name_dict["night"])
        city = self.city.extract(features, self.class_name_dict["city"])
        precipitation = self.precipitation.extract(features, self.class_name_dict["precipitation"])
        if precipitation[0] == "snowing":
            precipitation[0] = "snow"
        if precipitation[0] == "light_rain":
            precipitation[0] = "rain"

        metadata = [glare[0], night[0], city[0], precipitation[0]]
        return metadata

    def classname(self):
        if self.is_built == True:
            with open(pkg_resources.resource_filename("raymon", "models/weather/classes.json"), "w") as json_file:
                json.dump(self.class_name_dict, json_file)
                print("Created classes.json")
        elif os.path.isfile(pkg_resources.resource_filename("raymon", "models/weather/classes.json")):
            with open(pkg_resources.resource_filename("raymon", "models/weather/classes.json")) as f:
                classes = json.load(f)
            self.class_name_dict = classes
        else:
            classes = {
                "glare": {"0": "no_glare", "1": "glare"},
                "night": {"0": "day", "1": "night", "2": "twilight"},
                "city": {"0": "rural", "1": "urban"},
                "precipitation": {"0": "rain", "1": "snow", "2": "clear", "3": "light_rain", "4": "snowing"},
            }
            self.class_name_dict = classes
