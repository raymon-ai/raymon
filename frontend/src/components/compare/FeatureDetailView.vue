<template>
  <div class="schemaView mt-3">
    <h1> Feature: <span class="codeLike">{{componentName}} </span> </h1>
    <VuePlotly
      :data="plotData"
      :layout="plotLayout"
      :autoResize="false"
      :options="plotOptions"
    />

    <h1> Stats: </h1>

    <div class="tableWrapper hideScrollbar">
      <table>
        <thead>
          <tr>
            <th class="raytablehead nameColumn px-2">
              <label>Stat </label>

            </th>

            <th
              class="raytablehead typeColumn px-2 schemaInd"
              :style="{'border-left-color': blue}"
            >
              <label>{{schemaDef.name}}@{{schemaDef.version}} </label>
            </th>
            <th
              class="raytablehead typeColumn px-2 schemaInd"
              :style="{'border-left-color': red}"
            >
              <label>{{otherDef.name}}@{{otherDef.version}} </label>

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
            <td class="p-1 codeLike">
              {{getOtherStatValueFormatted(key)}}
            </td>
          </tr>

        </tbody>
      </table>

    </div>
    <div class="mt-4">
      <a
        href="#"
        @click="goToMainView"
      >Back</a>
    </div>
  </div>
</template>


<script>
const octicons = require("@primer/octicons");
import VuePlotly from "@statnett/vue-plotly";
import { red, green, blue, yellow } from "@/colors.js";
export default {
  components: { VuePlotly },
  props: ["schemaDef", "otherDef", "componentType", "componentName"],
  data: function () {
    return {
      red,
      green,
      blue,
      plotOptions: {
        staticPlot: false,
        displayModeBar: false,
      },
      statKeys: ["min", "max", "mean", "std", "pinv", "samplesize", "domain"],
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
      return this.schemaDef[this.componentType][this.componentName];
    },
    otherFeatureData() {
      return this.otherDef[this.componentType][this.componentName];
    },
    componentDataType() {
      const splits = this.componentData.component_class.split(".");
      return splits.slice(-1)[0];
    },

    stats() {
      return this.componentData.component.stats;
    },
    otherStats() {
      return this.otherFeatureData.component.stats;
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
    pinv() {
      return this.stats.pinv.toFixed(2);
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
    otherMin() {
      if (this.isNumeric) {
        return this.otherStats.min.toFixed(2);
      } else {
        return "NA";
      }
    },
    otherMax() {
      if (this.isNumeric) {
        return this.otherStats.max.toFixed(2);
      } else {
        return "NA";
      }
    },
    otherMean() {
      if (this.isNumeric) {
        return this.otherStats.mean.toFixed(2);
      } else {
        return "NA";
      }
    },
    otherStd() {
      if (this.isNumeric) {
        return this.otherStats.std.toFixed(2);
      } else {
        return "NA";
      }
    },
    otherPinv() {
      return this.otherStats.pinv.toFixed(2);
    },
    otherSamplesize() {
      return this.otherStats.samplesize;
    },
    otherDomain() {
      if (!this.isNumeric) {
        return Object.keys(this.otherStats.frequencies);
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
      } else if (key === "pinv") {
        return this.pinv;
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
    getOtherStatValueFormatted(key) {
      if (key === "min") {
        return this.otherMin;
      } else if (key === "max") {
        return this.otherMax;
      } else if (key === "pinv") {
        return this.otherPinv;
      } else if (key === "mean") {
        return this.otherMean;
      } else if (key === "std") {
        return this.otherStd;
      } else if (key === "samplesize") {
        return this.otherSamplesize;
      } else if (key === "domain") {
        return this.otherDomain;
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
            color: blue,
          },
          name: `${this.schemaDef.name}@${this.schemaDef.version}`,
        },
        {
          x: this.otherStats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: red,
          },
          name: `${this.otherDef.name}@${this.otherDef.version}`,
        },
      ];

      return plots;
    },
    getCategoricPlotData() {
      let domain = Object.keys(this.stats.frequencies);
      let counts = Object.values(this.stats.frequencies);

      let otherDomain = Object.keys(this.otherStats.frequencies);
      let otherCounts = Object.values(this.otherStats.frequencies);

      let plots = [
        {
          x: domain,
          y: counts,
          type: "bar",
          marker: {
            color: blue,
          },
          name: "distribution",
        },
        {
          x: otherDomain,
          y: otherCounts,
          type: "bar",
          marker: {
            color: red,
          },
        },
      ];

      return plots;
    },
  },
};
</script>

<style lang="scss">
.schemaInd {
  border-left: 10px;
  /* border-left-color: blue; */
  border-left-style: solid;
}
</style>
