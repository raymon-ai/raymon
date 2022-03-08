from sklearn import svm
from sklearn.utils import shuffle
import pickle
import os
import pkg_resources


class SVM:
    def __init__():
        pass

    def build(self, partname, features, targets=None):
        self.svm_model = svm.SVC(C=1.0, kernel="rbf")
        features, targets = shuffle(features, targets)
        self.svm_model.fit(features, targets)
        pickle.dump(
            self.svm_model, open(pkg_resources.resource_filename("raymon", "models/weather/" + partname + ".sav"), "wb")
        )
        print("Created SVM " + partname + " model")

    def extract(self, class_name_dict, features):
        results = self.svm_model.predict(features)
        metadata = [class_name_dict[str(label)] for label in results]
        return metadata
