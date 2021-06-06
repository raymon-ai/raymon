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
from raymon.profiling.components import Component, InputComponent, OutputComponent, ActualComponent, EvalComponent
from raymon.out import NoOutput, nullcontext

COMPONENT_TYPES = ["input_comps", "output_comps", "actual_comps", "eval_comps"]


class ModelProfile(Serializable, Buildable):

    _attrs = ["name", "version", "components"]

    def __init__(
        self,
        name="default",
        version="0.0.0",
        components={},
        summaries={},
    ):

        self._name = None
        self._version = None
        self._components = {}

        self.name = str(name)
        self.version = str(version)
        self.components = components

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
    def components(self):
        return self._components

    @components.setter
    def components(self, value):
        if isinstance(value, list) and all(isinstance(component, Component) for component in value):
            # Convert to dict
            self._components = {c.name: c for c in value}
        elif isinstance(value, dict) and all(isinstance(component, Component) for component in value.values()):
            self._components = value
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
        ser_comps = {}
        for component in self.components.values():
            ser_comps[component.name] = component.to_jcr()
        jcr["components"] = ser_comps
        return jcr

    @classmethod
    def from_jcr(cls, jcr, mock_extractors=False):
        name = jcr["name"]
        version = jcr["version"]

        components = {}
        for comp_dict in jcr["components"].values():
            component = Component.from_jcr(comp_dict, mock_extractor=mock_extractors)
            components[component.name] = component
        return cls(name=name, version=version, components=components)

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
            for component in self.components.values():
                comp_domain = domains.get(component.name, None)
                if isinstance(component, InputComponent):
                    component.build(data=input, domain=comp_domain)
                elif isinstance(component, OutputComponent):
                    component.build(data=output, domain=comp_domain)
                elif isinstance(component, ActualComponent):
                    component.build(data=actual, domain=comp_domain)
                elif isinstance(component, EvalComponent):
                    component.build(data=[output, actual])
                else:
                    raise ProfileStateException("Unknown Component type: ", type(component))

    def is_built(self):
        return all(component.is_built() for component in self.components.values())

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

    def _validate_simple(self, data, components, convert_json=True):
        tags = []
        if self.is_built():
            for component in components:
                component_tags = component.validate(data=data)
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
        components = [c for c in self.components if isinstance(c, InputComponent)]
        return self._validate_simple(data=input, components=components, convert_json=convert_json)

    def validate_output(self, output, convert_json=True):
        components = [c for c in self.components if isinstance(c, OutputComponent)]
        return self._validate_simple(data=input, components=components, convert_json=convert_json)

    def validate_actual(self, actual, convert_json=True):
        components = [c for c in self.components if isinstance(c, ActualComponent)]
        return self._validate_simple(data=input, components=components, convert_json=convert_json)

    def validate_eval(self, output, actual, convert_json=True):
        tags = []
        components = [c for c in self.components if isinstance(c, EvalComponent)]
        if self.is_built():
            for component in components:
                component_tags = component.validate(data=(output, actual))
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

        for component in self.components.values():
            print(component.name)
            comp_thresholds = thresholds.get(component.name, {})
            comp_report = component.contrast(
                other.components[component.name],
                thresholds=comp_thresholds,
            )
            report[component.name] = comp_report

        jcr = {}
        jcr["reference"] = self.to_jcr()
        jcr["alternativeA"] = other.to_jcr()
        jcr["report"] = report
        return jcr

    def contrast_alternatives(self, alternativeA, alternativeB, thresholds={}):
        if not self.is_built():
            raise ProfileStateException("Profile 'self' is not built.")
        if not alternativeA.is_built():
            raise ProfileStateException("Profile 'alternativeA' is not built.")
        if not alternativeB.is_built():
            raise ProfileStateException("Profile 'alternativeB' is not built.")
        report = {}
        for component in self.components.values():
            print(component.name)
            comp_thresholds = thresholds.get(component.name, {})

            comp_report = alternativeA.components[component.name].contrast(
                alternativeB.components[component.name],
                thresholds=comp_thresholds,
            )

            report[component.name] = comp_report

        jcr = {}
        jcr["reference"] = self.to_jcr()
        jcr["alternativeA"] = alternativeA.to_jcr()
        jcr["alternativeB"] = alternativeB.to_jcr()
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
                    <link href="https://unpkg.com/@primer/css@17.0.1/dist/primer.css" rel="stylesheet" />

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
                <link href="https://unpkg.com/@primer/css@17.0.1/dist/primer.css" rel="stylesheet" />

                <raymon-compare-schema-str comparison="{jsonescaped}"></raymon-compare-schema-str>
                """
        return self._build_page(htmlstr=htmlstr, mode=mode, outdir=outdir)

    def view_contrast_alternatives(
        self, alternativeA, alternativeB, mode="iframe", thresholds={}, outdir=None, silent=True
    ):
        if silent:
            ctx_mgr = NoOutput()
        else:
            ctx_mgr = nullcontext()
        # Build the schema
        with ctx_mgr:
            jcr = self.contrast_alternatives(alternativeA, alternativeB, thresholds=thresholds)
            jsonescaped = html.escape(json.dumps(jcr))
            htmlstr = f"""
                <meta charset="utf-8">
                <title>Raymon contrast</title>
                <script src="./raymon.min.js"></script>
                <link href="https://unpkg.com/@primer/css@17.0.1/dist/primer.css" rel="stylesheet" />

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
