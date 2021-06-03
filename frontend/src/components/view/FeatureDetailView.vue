<template>
  <div class="schemaView mt-3">
    <h2 class="h2 mt-4"> Feature: <span class="codeLike">{{componentName}} </span> </h2>
    <VuePlotly
      :data="plotData"
      :layout="plotLayout"
      :autoResize="false"
      :options="plotOptions"
    />

    <h2 class="h2 mt-4"> Stats: </h2>

    <div class="tableWrapper hideScrollbar">
      <table>
        <thead>
          <tr>
            <th class="raytablehead nameColumn px-2">
              <label>Stat </label>

            </th>

            <th class="raytablehead typeColumn px-2">
              <label>{{refDef.name}}@{{refDef.version}} </label>

            </th>

          </tr>
        </thead>
        <tbody>
          <tr
            v-for="key in statKeys"
            :key="key"
          >
            <td class="p-1 codeLike">
              {{key}}
            </td>
            <td class="p-1 codeLike">
              {{getStatValueFormatted(key)}}
            </td>
          </tr>

        </tbody>
      </table>

    </div>
    <div class="mt-2">
      <a
        href="#"
        @click="goToMainView"
        class="f3"
      >Back</a>
    </div>
  </div>
</template>


<script>
const octicons = require("@primer/octicons");
import VuePlotly from "@statnett/vue-plotly";
import { colors } from "@/js/colors.js";
export default {
  components: { VuePlotly },
  props: ["refDef", "poi", "componentType", "componentName"],
  data: function () {
    return {
      plotOptions: {
        staticPlot: false,
        displayModeBar: false,
      },
      statKeys: [
        "min",
        "max",
        "mean",
        "std",
        "invalids",
        "samplesize",
        "domain",
      ],
    };
  },
  computed: {
    plotLayout() {
      return {
        autosize: false,
        width: 900,
        height: 500,
        margin: {
          l: 50,
          r: 50,
          b: 50,
          t: 50,
          pad: 0,
        },
        xaxis: {
          title: this.componentName,
        },
        yaxis: {
          title: "cdf",
        },
      };
    },
    componentData() {
      return this.refDef[this.componentType][this.componentName];
    },
    componentDataType() {
      const splits = this.componentData.component_class.split(".");
      return splits.slice(-1)[0];
    },
    poiValue() {
      return this.poi[this.componentName];
    },
    stats() {
      return this.componentData.component.stats;
    },
    isNumeric() {
      return (
        this.componentDataType.toLowerCase() === "intcomponent" ||
        this.componentDataType.toLowerCase() === "floatcomponent"
      );
    },
    min() {
      if (this.isNumeric) {
        return this.stats.min.toFixed(2);
      } else {
        return "NA";
      }
    },
    max() {
      if (this.isNumeric) {
        return this.stats.max.toFixed(2);
      } else {
        return "NA";
      }
    },
    mean() {
      if (this.isNumeric) {
        return this.stats.mean.toFixed(2);
      } else {
        return "NA";
      }
    },
    std() {
      if (this.isNumeric) {
        return this.stats.std.toFixed(2);
      } else {
        return "NA";
      }
    },
    invalids() {
      return this.stats.invalids.toFixed(2);
    },
    samplesize() {
      return this.stats.samplesize;
    },
    domain() {
      if (!this.isNumeric) {
        return Object.keys(this.stats.frequencies);
      } else {
        return "NA";
      }
    },
    plotData() {
      if (this.isNumeric) {
        return this.getNumberPlotData();
      } else {
        return this.getCategoricPlotData();
      }
    },
  },
  methods: {
    goToMainView() {
      this.$emit("setPage", undefined);
    },
    getStatValueFormatted(key) {
      if (key === "min") {
        return this.min;
      } else if (key === "max") {
        return this.max;
      } else if (key === "invalids") {
        return this.invalids;
      } else if (key === "mean") {
        return this.mean;
      } else if (key === "std") {
        return this.std;
      } else if (key === "samplesize") {
        return this.samplesize;
      } else if (key === "domain") {
        return this.domain;
      } else {
        console.log("Unknown key: ", key);
      }
    },

    getNumberPlotData() {
      let plots = [
        {
          x: this.stats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: colors.color_scale_blue_5,
          },
          name: "cdf",
        },
      ];
      if (this.poiValue) {
        console.log("Poivalue: ", typeof this.poiValue);
        plots.push({
          x: [this.poiValue, this.poiValue],
          y: [0, 100],
          mode: "lines",
          line: {
            color: colors.color_scale_green_5,
            width: 1.5,
          },
          name: "poi",
        });
      }
      return plots;
    },
    getCategoricPlotData() {
      let domain = Object.keys(this.stats.frequencies);
      let counts = Object.values(this.stats.frequencies);

      let plots = [
        {
          x: domain,
          y: counts,
          type: "bar",
          marker: {
            color: colors.color_scale_blue_5,
          },
          name: "distribution",
        },
      ];
      if (this.poiValue) {
        plots.push({
          x: [this.poiValue, this.poiValue],
          y: [0, Math.max(...counts)],
          mode: "lines",
          line: {
            color: colors.color_scale_green_5,
            width: 1.5,
          },
          name: "poi",
        });
      }
      return plots;
    },
  },
};
</script>

<style>
</style>
