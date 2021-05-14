import json
import html
import json
import tempfile
import shutil
import webbrowser
import numbers

from pydoc import locate
from pathlib import Path

import raymon
from raymon.globals import Buildable, ProfileStateException, Serializable
from raymon.profiling.components import Component
from raymon.out import NoOutput, nullcontext

COMPONENT_TYPES = ["input_comps", "output_comps", "actual_comps", "eval_comps"]


class ModelProfile(Serializable, Buildable):

    _attrs = ["name", "version", "components"]

    def __init__(
        self,
        name="default",
        version="0.0.0",
        input_comps={},
        output_comps={},
        actual_comps={},
        eval_comps={},
        summaries={},
    ):
        """ModelProfiles are used to capture and guard input, output, actual and prediction score characteristics for ML models.

        Parameters
        ----------
        name : str
            Name of the profile
        version : str
            Version of the profile
        input_comps : dict or list
            A list of components that will check the inputs of the model.
        output_comps : dict or list
            A list of components that will check the outputs of the model.
        actual_comps : dict or list
            A list of components that will check the actuals of the model.
        eval_comps : dict or list
            A list of components that will score the models predictions using the outpus and actuals.
        """

        self._name = None
        self._version = None
        self._input_comps = {}
        self._output_comps = {}
        self._actual_comps = {}
        self._scoreing_comps = {}

        self.name = str(name)
        self.version = str(version)
        self.input_comps = input_comps
        self.output_comps = output_comps
        self.actual_comps = actual_comps
        self.eval_comps = eval_comps

    """Serializable interface"""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Profile name should be a string")
        if "@" in value:
            raise ValueError(f"Profile name should not include '@'")
        self._name = value.lower()

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Profile version should be a string")
        self._version = value

    @property
    def input_comps(self):
        return self._input_comps

    @input_comps.setter
    def input_comps(self, value):
        if isinstance(value, list) and all(isinstance(component, Component) for component in value):
            # Convert to dict
            self._input_comps = {c.name: c for c in value}
        elif isinstance(value, dict) and all(isinstance(component, Component) for component in value.values()):
            self._input_comps = value
        else:
            raise ValueError(f"components must be a list[Component] or dict[str, Component]")

    @property
    def output_comps(self):
        return self._output_comps

    @output_comps.setter
    def output_comps(self, value):
        if isinstance(value, list) and all(isinstance(component, Component) for component in value):
            # Convert to dict
            self._output_comps = {c.name: c for c in value}
        elif isinstance(value, dict) and all(isinstance(component, Component) for component in value.values()):
            self._output_comps = value
        else:
            raise ValueError(f"components must be a list[Component] or dict[str, Component]")

    @property
    def actual_comps(self):
        return self._actual_comps

    @actual_comps.setter
    def actual_comps(self, value):
        if isinstance(value, list) and all(isinstance(component, Component) for component in value):
            # Convert to dict
            self._actual_comps = {c.name: c for c in value}
        elif isinstance(value, dict) and all(isinstance(component, Component) for component in value.values()):
            self._actual_comps = value
        else:
            raise ValueError(f"components must be a list[Component] or dict[str, Component]")

    @property
    def eval_comps(self):
        return self._eval_comps

    @eval_comps.setter
    def eval_comps(self, value):
        if isinstance(value, list) and all(isinstance(component, Component) for component in value):
            # Convert to dict
            self._eval_comps = {c.name: c for c in value}
        elif isinstance(value, dict) and all(isinstance(component, Component) for component in value.values()):
            self._eval_comps = value
        else:
            raise ValueError(f"components must be a list[Component] or dict[str, Component]")

    @property
    def group_idfr(self):
        return f"{self.name}@{self.version}".lower()

    def to_jcr(self):
        jcr = {
            "name": self.name,
            "version": self.version,
        }
        for idfr in COMPONENT_TYPES:
            self_comps = getattr(self, idfr)
            ser_comps = {}
            for component in self_comps.values():
                ser_comps[component.name] = component.to_jcr()
            jcr[idfr] = ser_comps
        return jcr

    @classmethod
    def from_jcr(cls, jcr):
        name = jcr["name"]
        version = jcr["version"]
        comp_types = {}
        for idfr in COMPONENT_TYPES:
            components = {}
            for comp_dict in jcr[idfr].values():
                component = Component.from_jcr(comp_dict)
                components[component.name] = component
            comp_types[idfr] = components
        return cls(name=name, version=version, **comp_types)

    def save(self, dir):
        dir = Path(dir)
        fpath = dir / f"{self.name}@{self.version}.json"
        with open(fpath, "w") as f:
            json.dump(self.to_jcr(), f, indent=4)

    @classmethod
    def load(cls, fpath):
        with open(fpath, "r") as f:
            jcr = json.load(f)
        return cls.from_jcr(jcr)

    """Buildable Interface"""

    def build(self, input=None, output=None, actual=None, domains={}, silent=True):
        if silent:
            ctx_mgr = NoOutput()
        else:
            ctx_mgr = nullcontext()
        # Build the schema
        with ctx_mgr:
            for comp_type in COMPONENT_TYPES:
                for component in getattr(self, comp_type).values():
                    comp_domain = domains.get(comp_type, {}).get(component.name, None)
                    if comp_type == "input_comps":
                        component.build(data=input, domain=comp_domain)
                    elif comp_type == "output_comps":
                        component.build(data=output, domain=comp_domain)
                    elif comp_type == "actual_comps":
                        component.build(data=actual, domain=comp_domain)
                    else:
                        component.build(data=[output, actual])

    def is_built(self):
        # Check all components built
        type_checks = []
        for comp_type in COMPONENT_TYPES:
            type_checks.append(all(component.is_built() for component in getattr(self, comp_type).values()))
        return all(type_checks)

    """Other Methods"""

    def __str__(self):
        return f'ModelProfile(name="{self.name}", version="{self.version}"'

    def set_group(self, tags):
        for component_tag in tags:
            component_tag.group = self.group_idfr

    def drop_component(self, name, comp_type="input_component"):
        new_comps = [c for c in getattr(self, comp_type).values() if c.name != name]
        setattr(self, comp_type, new_comps)

    def flatten_tags(self, tags):
        tags_dict = {}
        for tag in tags:
            tags_dict[tag["name"]] = tag["value"]
        return tags_dict

    def _validate_simple(self, data, components, cgroup, convert_json=True):
        tags = []
        if self.is_built():
            for component in components.values():
                component_tags = component.validate(data=data, cgroup=cgroup)
                self.set_group(component_tags)
                tags.extend(component_tags)
        else:
            raise ProfileStateException(
                f"Cannot check data on an unbuilt profile. Check whether all components are built."
            )
        if convert_json:
            tags = [t.to_jcr() for t in tags]
        return tags

    def validate_input(self, input, convert_json=True):
        return self._validate_simple(
            data=input, components=self.input_comps, cgroup="input_comps", convert_json=convert_json
        )

    def validate_output(self, output, convert_json=True):
        return self._validate_simple(
            data=output, components=self.output_comps, cgroup="output_comps", convert_json=convert_json
        )

    def validate_actual(self, actual, convert_json=True):
        return self._validate_simple(
            data=actual, components=self.actual_comps, cgroup="actual_comps", convert_json=convert_json
        )

    def validate_score(self, output, actual, convert_json=True):
        tags = []
        if self.is_built():
            for component in self.eval_comps.values():
                component_tags = component.validate(data=(output, actual), cgroup="eval_comps")
                self.set_group(component_tags)
                tags.extend(component_tags)
        else:
            raise ProfileStateException(
                f"Cannot check data on an unbuilt profile. Check whether all components are built."
            )
        if convert_json:
            tags = [t.to_jcr() for t in tags]
        return tags

    def contrast(self, other, thresholds={}):
        if not self.is_built():
            raise ProfileStateException("Profile 'self' is not built.")
        if not other.is_built():
            raise ProfileStateException("Profile 'other' is not built.")
        report = {}
        for comp_type in COMPONENT_TYPES:
            self_comps = getattr(self, comp_type)
            other_comps = getattr(other, comp_type)
            comp_type_thresholds = thresholds.get(comp_type, {})
            type_report = {}
            for component in self_comps.values():
                print(component.name)
                comp_thresholds = comp_type_thresholds.get(component.name, {})

                comp_report = self_comps[component.name].contrast(
                    other_comps[component.name],
                    thresholds=comp_thresholds,
                )

                type_report[component.name] = comp_report
            report[comp_type] = type_report

        jcr = {}
        jcr["reference"] = self.to_jcr()
        jcr["other"] = other.to_jcr()
        jcr["report"] = report
        return jcr

    def view(self, poi=None, mode="iframe", outdir=None, silent=True):
        if silent:
            ctx_mgr = NoOutput()
        else:
            ctx_mgr = nullcontext()
        # Build the schema
        with ctx_mgr:
            if poi is not None:
                poi_dict = self.flatten_tags(self.validate_input(poi))
            else:
                poi_dict = {}
            jsonescaped = html.escape(json.dumps(self.to_jcr()))
            poiescaped = html.escape(json.dumps(poi_dict))
            htmlstr = f"""
                    <meta charset="utf-8">
                    <title>Raymon view</title>
                    <script src="./raymon.min.js"></script>
                    <body>
                    <raymon-view-schema-str profile="{jsonescaped}" poi="{poiescaped}"></raymon-view-schema-str>
                    </body>
                    """
            return self._build_page(htmlstr=htmlstr, mode=mode, outdir=outdir)

    def view_contrast(self, other, mode="iframe", thresholds={}, outdir=None, silent=True):
        if silent:
            ctx_mgr = NoOutput()
        else:
            ctx_mgr = nullcontext()
        # Build the schema
        with ctx_mgr:
            jcr = self.contrast(other, thresholds=thresholds)
            jsonescaped = html.escape(json.dumps(jcr))
            htmlstr = f"""
                <meta charset="utf-8">
                <title>Raymon contrast</title>
                <script src="./raymon.min.js"></script>
                <raymon-compare-schema-str comparison="{jsonescaped}"></raymon-compare-schema-str>
                """
        return self._build_page(htmlstr=htmlstr, mode=mode, outdir=outdir)

    def _build_page(self, htmlstr, mode="iframe", outdir=None):
        frontend_src = (Path(raymon.__file__) / "../frontend/").resolve()
        print(f"Frontend src: {frontend_src}")
        tmp_dir = Path(tempfile.mkdtemp(dir=outdir, prefix=".tmp")) / "view"
        shutil.copytree(src=frontend_src, dst=tmp_dir)
        html_file = tmp_dir / "schema.html"

        with open(html_file, "w") as f:
            f.write(htmlstr)
        if mode == "external":
            webbrowser.open_new_tab("file://" + str(html_file))

        return html_file
