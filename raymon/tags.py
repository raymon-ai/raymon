import string
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

CTYPE_TAGTYPES = {
    "input": {"tagtype": PROFILE_INPUT, "errortype": PROFILE_INPUT_ERROR},
    "output": {"tagtype": PROFILE_OUTPUT, "errortype": PROFILE_OUTPUT_ERROR},
    "actual": {"tagtype": PROFILE_ACTUAL, "errortype": PROFILE_ACTUAL_ERROR},
    "eval": {"tagtype": PROFILE_SCORE, "errortype": PROFILE_SCORE_ERROR},
}

ERROR_TYPES = [PROFILE_INPUT_ERROR, PROFILE_OUTPUT_ERROR, PROFILE_ACTUAL_ERROR, PROFILE_SCORE_ERROR]


def normalize(tag_name):
    tag_nospaces = tag_name.replace(" ", "_").lower()
    allowed_chars = string.ascii_lowercase + string.digits + "_-@./"
    filtered = [c for c in tag_nospaces if c in allowed_chars]
    return "".join(filtered).rstrip("_")


def convert_tags(tags, format="tag"):
    if format == "tag":
        return tags
    elif format == "jcr":
        return [t.to_jcr() for t in tags]
    elif format == "simple":
        return {t.name: t.value for t in tags}


def filter_errors(tags, format="tag"):
    returnval = []
    for t in tags:
        if isinstance(t, Tag) and t.type in ERROR_TYPES:
            returnval.append(t)
        elif isinstance(t, dict) and t.get("type", None) in ERROR_TYPES:
            returnval.append(t)

    return convert_tags(returnval, format=format)


def flatten_jcr(tags):
    return {tag["name"]: tag["value"] for tag in tags}


class Tag(Serializable):
    """
    Represents a tag. Tags are used for monitoring and filtering in the backend.

    Parameters
    ----------
    name : str
        Name of the tag
    value : str or Number
        Value of the tag. Can be numeric or string.
    type : str
        Type of the tag. Note: some type string have a special meaning like tags assicuiated with data profiles and errors.
    group : str, optional
        y setting the group, you can indicate that this tag belongs to a certai nset of tagt. For example, all tags that belong to a certai ndata profile will have the same group.
    """

    def __init__(self, name, value, type, group=None):

        self.name = name
        self.value = value
        self.type = type
        self.group = group

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Profile name should be a string")
        value_normed = normalize(value)
        self._name = value_normed.lower()

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
