from enum import Enum

from raymon.globals import Serializable

PROFILE_INPUT = "profile-input"
PROFILE_OUTPUT = "profile-output"
PROFILE_ACTUAL = "profile-actual"
PROFILE_SCORE = "profile-score"
PROFILE_INPUT_ERROR = "profile-input-error"
PROFILE_OUTPUT_ERROR = "profile-output-error"
PROFILE_ACTUAL_ERROR = "profile-actual-error"
PROFILE_SCORE_ERROR = "profile-score-error"

LABEL = "label"
METRIC = "metric"
VECTOR = "vector"
ERROR = "error"

CGROUP_TAGTYPES = {
    "input_components": {"tagtype": PROFILE_INPUT, "errortype": PROFILE_INPUT_ERROR},
    "output_components": {"tagtype": PROFILE_OUTPUT, "errortype": PROFILE_OUTPUT_ERROR},
    "actual_components": {"tagtype": PROFILE_ACTUAL, "errortype": PROFILE_ACTUAL_ERROR},
    "score_components": {"tagtype": PROFILE_SCORE, "errortype": PROFILE_SCORE_ERROR},
}


class Tag(Serializable):
    def __init__(self, name, value, type, group=None):
        self.name = name
        self.value = value
        self.type = type
        self.group = group

    def to_jcr(self):
        jcr = {
            "type": self.type,
            "name": self.name,
            "value": self.value,
            "group": self.group,
        }
        return jcr

    @classmethod
    def from_jcr(cls, jcr):
        return cls(**jcr)

    def __str__(self):
        return f"'{self.name}:{self.value}"

    def __repr__(self):
        return f"Tag(name='{self.name}, value={self.value}, type={self.type}, group={self.group}"
