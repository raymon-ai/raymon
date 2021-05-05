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

COMPONENT_TYPES = ["input_components", "output_components", "actual_components", "score_components"]


class ModelProfile(Serializable, Buildable):
    _attrs = ["name", "version", "components"]

    def __init__(
        self,
        name="default",
        version="0.0.0",
        input_components={},
        output_components={},
        actual_components={},
        score_components={},
        summaries={},
    ):

        self._name = None
        self._version = None
        self._input_components = {}
        self._output_components = {}
        self._actual_components = {}
        self._scoreing_components = {}

        self.name = str(name)
        self.version = str(version)
        self.input_components = input_components
        self.output_components = output_components
        self.actual_components = actual_components
        self.score_components = score_components

    """Serializable interface"""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Schema name should be a string")
        self._name = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Schema version should be a string")
        self._version = value

    @property
    def input_components(self):
        return self._input_components

    @input_components.setter
    def input_components(self, value):
        if isinstance(value, list) and all(isinstance(component, Component) for component in value):
            # Convert to dict
            self._input_components = {c.name: c for c in value}
        elif isinstance(value, dict) and all(isinstance(component, Component) for component in value.values()):
            self._input_components = value
        else:
            raise ValueError(f"components must be a list[Component] or dict[str, Component]")

    @property
    def output_components(self):
        return self._output_components

    @output_components.setter
    def output_components(self, value):
        if isinstance(value, list) and all(isinstance(component, Component) for component in value):
            # Convert to dict
            self._output_components = {c.name: c for c in value}
        elif isinstance(value, dict) and all(isinstance(component, Component) for component in value.values()):
            self._output_components = value
        else:
            raise ValueError(f"components must be a list[Component] or dict[str, Component]")

    @property
    def actual_components(self):
        return self._actual_components

    @actual_components.setter
    def actual_components(self, value):
        if isinstance(value, list) and all(isinstance(component, Component) for component in value):
            # Convert to dict
            self._actual_components = {c.name: c for c in value}
        elif isinstance(value, dict) and all(isinstance(component, Component) for component in value.values()):
            self._actual_components = value
        else:
            raise ValueError(f"components must be a list[Component] or dict[str, Component]")

    @property
    def score_components(self):
        return self._score_components

    @score_components.setter
    def score_components(self, value):
        if isinstance(value, list) and all(isinstance(component, Component) for component in value):
            # Convert to dict
            self._score_components = {c.name: c for c in value}
        elif isinstance(value, dict) and all(isinstance(component, Component) for component in value.values()):
            self._score_components = value
        else:
            raise ValueError(f"components must be a list[Component] or dict[str, Component]")

    @property
    def group_idfr(self):
        return f"{self.name}@{self.version}"

    def to_jcr(self):
        jcr = {
            "name": self.name,
            "version": self.version,
        }
        for idfr in COMPONENT_TYPES:
            self_components = getattr(self, idfr)
            ser_components = {}
            for component in self_components.values():
                ser_components[component.name] = component.to_jcr()
            jcr[idfr] = ser_components
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

    def save(self, fpath):
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
                    if comp_type == "input_components":
                        component.build(data=input, domain=comp_domain)
                    elif comp_type == "output_components":
                        component.build(data=output, domain=comp_domain)
                    elif comp_type == "actual_components":
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
        new_components = [c for c in getattr(self, comp_type).values() if c.name != name]
        setattr(self, comp_type, new_components)

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
            data=input, components=self.input_components, cgroup="input_components", convert_json=convert_json
        )

    def validate_output(self, output, convert_json=True):
        return self._validate_simple(
            data=output, components=self.output_components, cgroup="output_components", convert_json=convert_json
        )

    def validate_actual(self, actual, convert_json=True):
        return self._validate_simple(
            data=actual, components=self.actual_components, cgroup="actual_components", convert_json=convert_json
        )

    def validate_score(self, output, actual, convert_json=True):
        tags = []
        if self.is_built():
            for component in self.score_components.values():
                component_tags = component.validate(data=(output, actual), cgroup="score_components")
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
            self_components = getattr(self, comp_type)
            other_components = getattr(other, comp_type)
            comp_type_thresholds = thresholds.get(comp_type, {})
            type_report = {}
            for component in self_components.values():
                print(component.name)
                ref_stats = self_components[component.name].stats
                other_stats = other_components[component.name].stats
                comp_thresholds = comp_type_thresholds.get(component.name, {})
                int_threshold = comp_thresholds.get("integrity", 0.01)
                drift_threshold = comp_thresholds.get("drift", 0.05)
                drift, drift_idx, pinvdiff = ref_stats.contrast(other_stats)
                drift_report = {
                    "drift": float(drift),
                    "drift_idx": drift_idx,
                    "weight": float(self_components[component.name].importance * drift),
                    "alert": int(drift >= drift_threshold),
                }
                integrity_report = {
                    "weight": float(self_components[component.name].importance * pinvdiff),
                    "integrity": float(pinvdiff),
                    "alert": int(pinvdiff >= int_threshold),
                }
                type_report[component.name] = {"drift": drift_report, "integrity": integrity_report}
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
                    <title>raymon-schema-view demo</title>
                    <script src="./raymon.min.js"></script>
                    <body>
                    <raymon-view-schema schema="{jsonescaped}" poi="{poiescaped}"></raymon-view-schema>
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
                <title>raymon-schema-view demo</title>
                <script src="./raymon.min.js"></script>
                <raymon-compare-schema comparison="{jsonescaped}"></raymon-compare-schema>
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
