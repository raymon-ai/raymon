import json
import html
import json
import tempfile
import shutil
import webbrowser
import numbers

from pydoc import locate
from pathlib import Path
import pkg_resources
import raymon
from raymon.globals import Buildable, ProfileStateException, Serializable
from raymon.profiling.components import Component, InputComponent, OutputComponent, ActualComponent, EvalComponent
from raymon.profiling.reducers import Reducer
from raymon.out import NoOutput, nullcontext


class ModelProfile(Serializable, Buildable):

    _attrs = ["name", "version", "components"]

    def __init__(
        self,
        name="default",
        version="0.0.0",
        components={},
        reducers={},
    ):

        self._name = None
        self._version = None
        self._components = {}
        self._reducers = {}

        self.name = str(name)
        self.version = str(version)
        self.components = components
        self.reducers = reducers

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
    def reducers(self):
        return self._reducers

    @reducers.setter
    def reducers(self, value):
        if isinstance(value, list) and all(isinstance(reducers, Reducer) for reducers in value):
            # Convert to dict
            self._reducers = {c.name: c for c in value}
        elif isinstance(value, dict) and all(isinstance(reducers, Reducer) for reducers in value.values()):
            self._reducers = value
        else:
            raise ValueError(f"components must be a list[Reducer] or dict[str, Reducer]")

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
        # likewise for reducers
        ser_reducers = {}
        for reducer in self.reducers.values():
            ser_reducers[reducer.name] = reducer.to_jcr()
        jcr["reducers"] = ser_reducers
        return jcr

    @classmethod
    def from_jcr(cls, jcr, mock_extractors=False):
        name = jcr["name"]
        version = jcr["version"]

        components = {}
        for comp_dict in jcr["components"].values():
            component = Component.from_jcr(comp_dict, mock_extractor=mock_extractors)
            components[component.name] = component
        # TODO: likewise for reducers
        reducers = {}
        for reducer_dict in jcr["reducers"].values():
            reducer = Reducer.from_jcr(reducer_dict)
            reducers[reducer.name] = reducer
        return cls(name=name, version=version, components=components, reducers=reducers)

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
            component_values = {}
            for component in self.components.values():
                print(component.name)
                comp_domain = domains.get(component.name, None)
                if isinstance(component, InputComponent):
                    values = component.build(data=input, domain=comp_domain)
                elif isinstance(component, OutputComponent):
                    values = component.build(data=output, domain=comp_domain)
                elif isinstance(component, ActualComponent):
                    values = component.build(data=actual, domain=comp_domain)
                elif isinstance(component, EvalComponent):
                    values = component.build(data=[output, actual])
                else:
                    raise ProfileStateException("Unknown Component type: ", type(component))
                component_values[component.name] = values

            for reducer in self.reducers.values():
                reducer.build(data=component_values)

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
        components = [c for c in self.components.values() if isinstance(c, InputComponent)]
        return self._validate_simple(data=input, components=components, convert_json=convert_json)

    def validate_output(self, output, convert_json=True):
        components = [c for c in self.components.values() if isinstance(c, OutputComponent)]
        return self._validate_simple(data=output, components=components, convert_json=convert_json)

    def validate_actual(self, actual, convert_json=True):
        components = [c for c in self.components.values() if isinstance(c, ActualComponent)]
        return self._validate_simple(data=actual, components=components, convert_json=convert_json)

    def validate_eval(self, output, actual, convert_json=True):
        tags = []
        components = [c for c in self.components.values() if isinstance(c, EvalComponent)]
        if self.is_built():
            for component in components:
                component_tags = component.validate(data=(output, actual))
                print(component_tags)
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
        # if not self.is_built():
        #     raise ProfileStateException("Profile 'self' is not built.")
        # if not other.is_built():
        #     raise ProfileStateException("Profile 'other' is not built.")
        component_thresholds = thresholds.get("components", {})
        reducer_thresholds = thresholds.get("reducers", {})
        report = {}
        for component in self.components.values():
            if component.name not in other.components:
                print(f"Component {component.name} not found in other, skipping...")
                continue
            comp_thresholds = component_thresholds.get(component.name, {})
            comp_report = component.contrast(
                other.components[component.name],
                thresholds=comp_thresholds,
            )
            report[component.name] = comp_report

        reducer_reports = {}
        for reducer in self.reducers.values():
            red_threshold = reducer_thresholds.get(reducer.name, {})
            if reducer.name not in other.reducers:
                print(f"Reducer {reducer.name} not found in other, skipping...")
                continue
            red_report = reducer.contrast(
                other.reducers[reducer.name], components=self.components, thresholds=red_threshold
            )
            reducer_reports[reducer.name] = red_report

        jcr = {}
        jcr["reference"] = self.to_jcr()
        jcr["alternativeA"] = other.to_jcr()
        jcr["health_reports"] = report
        jcr["reducer_reports"] = reducer_reports
        return jcr

    def contrast_alternatives(self, alternativeA, alternativeB, thresholds={}):
        # if not self.is_built():
        #     raise ProfileStateException("Profile 'self' is not built.")
        # if not alternativeA.is_built():
        #     raise ProfileStateException("Profile 'alternativeA' is not built.")
        # if not alternativeB.is_built():
        #     raise ProfileStateException("Profile 'alternativeB' is not built.")
        component_thresholds = thresholds.get("components", {})
        reducer_thresholds = thresholds.get("reducers", {})
        report = {}
        for component in self.components.values():
            print(component.name)
            comp_thresholds = component_thresholds.get(component.name, {})
            if component.name not in alternativeA.components:
                print(f"Component {component.name} not found in alternativeA, skipping...")
                continue
            if component.name not in alternativeB.components:
                print(f"Component {component.name} not found in alternativeB, skipping...")
                continue
            comp_report = alternativeA.components[component.name].contrast(
                alternativeB.components[component.name],
                thresholds=comp_thresholds,
            )
            report[component.name] = comp_report

        reducer_reports = {}
        for reducer in self.reducers.values():
            red_threshold = reducer_thresholds.get(reducer.name, {})
            if reducer.name not in alternativeA.reducers:
                print(f"Reducer {reducer.name} not found in alternativeA, skipping...")
                continue
            if reducer.name not in alternativeB.reducers:
                print(f"Reducer {reducer.name} not found in alternativeB, skipping...")
                continue
            red_report = alternativeA.reducers[reducer.name].contrast(
                alternativeB.reducers[reducer.name], components=alternativeA.components, thresholds=red_threshold
            )
            reducer_reports[reducer.name] = red_report

        jcr = {}
        jcr["reference"] = self.to_jcr()
        jcr["alternativeA"] = alternativeA.to_jcr()
        jcr["alternativeB"] = alternativeB.to_jcr()
        jcr["health_reports"] = report
        jcr["reducer_reports"] = reducer_reports
        return jcr

    def view(self, poi=None, mode="external", outdir=None, silent=True):
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

    def view_contrast(self, other, mode="external", thresholds={}, outdir=None, silent=True):
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
                <body>
                <raymon-compare-schema-str comparison="{jsonescaped}"></raymon-compare-schema-str>
                </body>
                """
        return self._build_page(htmlstr=htmlstr, mode=mode, outdir=outdir)

    def view_contrast_alternatives(
        self, alternativeA, alternativeB, mode="external", thresholds={}, outdir=None, silent=True
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
                <body>
                <raymon-compare-schema-str comparison="{jsonescaped}"></raymon-compare-schema-str>
                </body>
                """
        return self._build_page(htmlstr=htmlstr, mode=mode, outdir=outdir)

    def _build_page(self, htmlstr, mode="external", outdir=None):
        tmp_dir = Path(tempfile.mkdtemp(dir=outdir, prefix=".tmp"))
        shutil.copy(src=pkg_resources.resource_filename("raymon", "frontend/raymon.min.js"), dst=tmp_dir)
        shutil.copy(src=pkg_resources.resource_filename("raymon", "frontend/raymon.min.js.map"), dst=tmp_dir)

        html_file = tmp_dir / "schema.html"

        with open(html_file, "w") as f:
            f.write(htmlstr)
        if mode == "external":
            webbrowser.open_new_tab("file://" + str(html_file))

        return html_file
