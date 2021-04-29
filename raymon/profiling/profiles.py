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
from raymon.tags import PROFILE_FEATURE
from raymon.profiling.components import Component
from raymon.out import NoOutput, nullcontext


class DataProfile(Serializable, Buildable):
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
        return f"{self.name}@{self.version}"

    def to_jcr(self):
        jcr = {
            "name": self.name,
            "version": self.version,
            "components": None,
        }
        components = {}
        for component in self.components.values():
            components[component.name] = component.to_jcr()
        jcr["components"] = components
        return jcr

    @classmethod
    def from_jcr(cls, jcr):
        name = jcr["name"]
        version = jcr["version"]
        components = {}
        for comp_dict in jcr["components"].values():
            component = Component.from_jcr(comp_dict)
            components[component.name] = component

        return cls(name=name, version=version, components=components)

    def save(self, fpath):
        with open(fpath, "w") as f:
            json.dump(self.to_jcr(), f, indent=4)

    @classmethod
    def load(cls, fpath):
        with open(fpath, "r") as f:
            jcr = json.load(f)
        return cls.from_jcr(jcr)

    """Buildable Interface"""

    def build(self, inputs, outputs, actuals, silent=True):
        if silent:
            ctx_mgr = NoOutput()
        else:
            ctx_mgr = nullcontext()
        # Build the schema
        with ctx_mgr:
            for name, component in self.components.items():
                # Compile stats
                component.build(inputs=inputs, outputs=outputs, actuals=actuals)

    def is_built(self):
        return all(component.is_built() for component in self.components.values())

    """Other Methods"""

    def __str__(self):
        return f'DataProfile(name="{self.name}", version="{self.version}"'

    def set_group(self, tags):
        for component_tag in tags:
            component_tag.group = self.group_idfr

    def check(self, data, convert_json=True):
        tags = []
        if self.is_built():
            for component in self.components.values():
                component_tags = component.check(data)
                self.set_group(component_tags)
                tags.extend(component_tags)
        else:
            raise ProfileStateException(
                f"Cannot check data on an unbuilt schema. Check whether all components are built."
            )
        if convert_json:
            tags = [t.to_jcr() for t in tags]
        return tags

    def drop_component(self, name):
        self.components = [c for c in self.components.values() if c.name != name]

    def flatten_tags(self, tags):
        tags_dict = {}
        for tag in tags:
            if tag["type"] == PROFILE_FEATURE:
                tags_dict[tag["name"]] = tag["value"]
        return tags_dict

    def _build_page(self, htmlstr, mode="iframe", outdir=None):
        frontend_src = (Path(raymon.__file__) / "../frontend/").resolve()
        tmp_dir = Path(tempfile.mkdtemp(dir=outdir, prefix=".tmp")) / "view"
        shutil.copytree(src=frontend_src, dst=tmp_dir)
        html_file = tmp_dir / "schema.html"

        with open(html_file, "w") as f:
            f.write(htmlstr)
        if mode == "external":
            webbrowser.open_new_tab("file://" + str(html_file))

        return html_file

    def view(self, poi=None, mode="iframe", outdir=None, silent=True):
        if silent:
            ctx_mgr = NoOutput()
        else:
            ctx_mgr = nullcontext()
        # Build the schema
        with ctx_mgr:
            if poi is not None:
                poi_dict = self.flatten_tags(self.check(poi))
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

    def test_drift(self, other, thresh_drift=0.05, thresh_inv=0.05):
        jcr = {}
        jcr["self"] = self.to_jcr()
        jcr["other"] = other.to_jcr()
        stats = {}
        drift_alerts = 0
        pinv_alerts = 0
        for componentname in self.components:
            print(componentname)
            drift, drift_idx, alert_drift, pinvdiff, alert_inv = self.components[componentname].stats.test_drift(
                other.components[componentname].stats, thresh_drift=thresh_drift, thresh_inv=thresh_inv
            )
            stats[componentname] = {
                "alert_drift": str(alert_drift),
                "drift": float(drift),
                "drift_idx": drift_idx,
                "impact": float(self.components[componentname].importance * drift),
                "pinvdiff": float(pinvdiff),
                "alert_inv": str(alert_inv),
            }
            if alert_drift:
                drift_alerts += 1
            if alert_inv:
                pinv_alerts += 1

        jcr["component_drift"] = stats
        jcr["health"] = {"drift_alerts": drift_alerts, "invalid_alerts": pinv_alerts, "total": len(self.components)}

        return jcr

    def compare(self, other, thresh=0.05, mode="iframe", outdir=None, silent=True):
        if silent:
            ctx_mgr = NoOutput()
        else:
            ctx_mgr = nullcontext()
        # Build the schema
        with ctx_mgr:
            jcr = self.test_drift(other, thresh=thresh)
            jsonescaped = html.escape(json.dumps(jcr))
            htmlstr = f"""
                <meta charset="utf-8">
                <title>raymon-schema-view demo</title>
                <script src="./raymon.min.js"></script>
                <raymon-compare-schema comparison="{jsonescaped}"></raymon-compare-schema>
                """
        return self._build_page(htmlstr=htmlstr, mode=mode, outdir=outdir)
