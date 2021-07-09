<template>
  <div class="schemaView mt-3">
    <h2 class="h2 mt-4"> Feature: <span class="codeLike">{{componentName}} </span> </h2>
    <VuePlotly
      :data="plotData"
      :layout="plotLayout"
      :autoResize="false"
      :options="plotOptions"
    />

    <h2 class="h2"> Stats: </h2>

    <div class="tableWrapper hideScrollbar">
      <table>
        <thead>
          <tr>
            <th class="raytablehead nameColumn px-2">
              <label>Stat </label>

            </th>

            <th
              class="raytablehead typeColumn px-2 schemaInd"
              :style="{'border-left-color': colors.color_scale_gray_5}"
            >
              <label>{{refData.name}}@{{refData.version}} </label>
            </th>
            <th
              class="raytablehead typeColumn px-2 schemaInd"
              :style="{'border-left-color': colors.color_scale_blue_5}"
            >
              <label>{{alternativeA.name}}@{{alternativeA.version}} </label>

            </th>
            <th
              v-if="alternativeB"
              class="raytablehead typeColumn px-2 schemaInd"
              :style="{'border-left-color': colors.color_scale_red_5}"
            >
              <label>{{alternativeB.name}}@{{alternativeB.version}} </label>

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
              {{getAlternativeAStatValueFormatted(key)}}
            </td>
            <td
              v-if="alternativeB"
              class="p-1 codeLike"
            >
              {{getAlternativeBStatValueFormatted(key)}}
            </td>
          </tr>

        </tbody>
      </table>

    </div>
    <div class="mt-4">
      <a
        href="#"
        class="f3"
        @click="goToMainView"
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
  props: [
    "refData",
    "alternativeA",
    "alternativeB",
    "componentType",
    "componentName",
  ],
  data: function () {
    return {
      colors,
      plotOptions: {
        staticPlot: false,
        displayModeBar: true,
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
        showlegend: true,
      };
    },

    componentData() {
      return this.refData.components[this.componentName];
    },
    alternativeAFeatureData() {
      return this.alternativeA.components[this.componentName];
    },
    alternativeBFeatureData() {
      if (this.alternativeB) {
        return this.alternativeB.components[this.componentName];
      } else {
        return undefined;
      }
    },
    componentDataType() {
      return this.componentData.state.dtype.toLowerCase();
    },

    refStats() {
      return this.componentData.state.stats.state;
    },
    alternativeAStats() {
      return this.alternativeAFeatureData.state.stats.state;
    },
    alternativeBStats() {
      if (this.alternativeBFeatureData) {
        return this.alternativeBFeatureData.state.stats.state;
      } else {
        return undefined;
      }
    },

    isNumeric() {
      return (
        this.componentDataType.toLowerCase() === "int" ||
        this.componentDataType.toLowerCase() === "float"
      );
    },
    min() {
      if (this.isNumeric) {
        return this.refStats.min.toFixed(2);
      } else {
        return "NA";
      }
    },
    max() {
      if (this.isNumeric) {
        return this.refStats.max.toFixed(2);
      } else {
        return "NA";
      }
    },
    mean() {
      if (this.isNumeric) {
        return this.refStats.mean.toFixed(2);
      } else {
        return "NA";
      }
    },
    std() {
      if (this.isNumeric) {
        return this.refStats.std.toFixed(2);
      } else {
        return "NA";
      }
    },
    invalids() {
      return this.refStats.invalids.toFixed(2);
    },
    samplesize() {
      return this.refStats.samplesize;
    },
    domain() {
      if (!this.isNumeric) {
        return Object.keys(this.refStats.frequencies);
      } else {
        return "NA";
      }
    },
    alternativeAMin() {
      if (this.isNumeric) {
        return this.alternativeAStats.min.toFixed(2);
      } else {
        return "NA";
      }
    },
    alternativeAMax() {
      if (this.isNumeric) {
        return this.alternativeAStats.max.toFixed(2);
      } else {
        return "NA";
      }
    },
    alternativeAMean() {
      if (this.isNumeric) {
        return this.alternativeAStats.mean.toFixed(2);
      } else {
        return "NA";
      }
    },
    alternativeAStd() {
      if (this.isNumeric) {
        return this.alternativeAStats.std.toFixed(2);
      } else {
        return "NA";
      }
    },
    alternativeAPinv() {
      return this.alternativeAStats.invalids.toFixed(2);
    },
    alternativeASamplesize() {
      return this.alternativeAStats.samplesize;
    },
    alternativeADomain() {
      if (!this.isNumeric) {
        return Object.keys(this.alternativeAStats.frequencies);
      } else {
        return "NA";
      }
    },
    alternativeBMin() {
      if (this.isNumeric) {
        return this.alternativeBStats.min.toFixed(2);
      } else {
        return "NA";
      }
    },
    alternativeBMax() {
      if (this.isNumeric) {
        return this.alternativeBStats.max.toFixed(2);
      } else {
        return "NA";
      }
    },
    alternativeBMean() {
      if (this.isNumeric) {
        return this.alternativeBStats.mean.toFixed(2);
      } else {
        return "NA";
      }
    },
    alternativeBStd() {
      if (this.isNumeric) {
        return this.alternativeBStats.std.toFixed(2);
      } else {
        return "NA";
      }
    },
    alternativeBPinv() {
      return this.alternativeBStats.invalids.toFixed(2);
    },
    alternativeBSamplesize() {
      return this.alternativeBStats.samplesize;
    },
    alternativeBDomain() {
      if (!this.isNumeric) {
        return Object.keys(this.alternativeAStats.frequencies);
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
    getAlternativeAStatValueFormatted(key) {
      if (key === "min") {
        return this.alternativeAMin;
      } else if (key === "max") {
        return this.alternativeAMax;
      } else if (key === "invalids") {
        return this.alternativeAPinv;
      } else if (key === "mean") {
        return this.alternativeAMean;
      } else if (key === "std") {
        return this.alternativeAStd;
      } else if (key === "samplesize") {
        return this.alternativeASamplesize;
      } else if (key === "domain") {
        return this.alternativeADomain;
      } else {
        console.log("Unknown key: ", key);
      }
    },
    getAlternativeBStatValueFormatted(key) {
      if (key === "min") {
        return this.alternativeBMin;
      } else if (key === "max") {
        return this.alternativeBMax;
      } else if (key === "invalids") {
        return this.alternativeBPinv;
      } else if (key === "mean") {
        return this.alternativeBMean;
      } else if (key === "std") {
        return this.alternativeBStd;
      } else if (key === "samplesize") {
        return this.alternativeBSamplesize;
      } else if (key === "domain") {
        return this.alternativeBDomain;
      } else {
        console.log("Unknown key: ", key);
      }
    },
    getNumberPlotData() {
      let plots = [
        {
          x: this.refStats.percentiles.concat(
            this.refStats.percentiles.slice().reverse()
          ),
          y: this.refStats.percentiles_lb.concat(
            this.refStats.percentiles_ub.slice().reverse()
          ),
          fill: "toself",
          fillcolor: "rgba(106, 115, 125, 0.2)", // same gray, but lower opacity
          line: {
            color: "transparent",
          },
          hoverinfo: "skip",
          showlegend: false,
        },
        {
          x: this.refStats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: colors.color_scale_gray_5,
          },
          name: `${this.refData.name}@${this.refData.version}`,
        },
        {
          x: this.alternativeAStats.percentiles.concat(
            this.alternativeAStats.percentiles.slice().reverse()
          ),
          y: this.alternativeAStats.percentiles_lb.concat(
            this.alternativeAStats.percentiles_ub.slice().reverse()
          ),
          fill: "toself",
          fillcolor: "rgba(3, 102, 214, 0.2)", // same blue, but lower opacity
          line: {
            color: "transparent",
          },
          hoverinfo: "skip",
          showlegend: false,
        },
        {
          x: this.alternativeAStats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: colors.color_scale_blue_5,
          },
          name: `${this.alternativeA.name}@${this.alternativeA.version}`,
        },
      ];
      if (this.alternativeB) {
        plots.push({
          x: this.alternativeBStats.percentiles.concat(
            this.alternativeBStats.percentiles.slice().reverse()
          ),
          y: this.alternativeBStats.percentiles_lb.concat(
            this.alternativeBStats.percentiles_ub.slice().reverse()
          ),
          fill: "toself",
          fillcolor: "rgba(215, 58, 73, 0.2)", // same red, but lower opacity
          line: {
            color: "transparent",
          },
          hoverinfo: "skip",
          showlegend: false,
        });
        plots.push({
          x: this.alternativeBStats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: colors.color_scale_red_5,
          },
          name: `${this.alternativeB.name}@${this.alternativeB.version}`,
        });
      }

      return plots;
    },
    getCategoricPlotData() {
      let domain = Object.keys(this.refStats.frequencies);
      let counts = Object.values(this.refStats.frequencies);
      let errors = [];
      for (const [key, value] of Object.entries(this.refStats.frequencies_lb)) {
        errors.push(this.refStats.frequencies[key] - value);
      }
      let alternativeADomain = Object.keys(this.alternativeAStats.frequencies);
      let alternativeACounts = Object.values(
        this.alternativeAStats.frequencies
      );
      let alternativeAErrors = [];
      for (const [key, value] of Object.entries(
        this.alternativeAStats.frequencies_lb
      )) {
        alternativeAErrors.push(
          this.alternativeAStats.frequencies[key] - value
        );
      }
      let plots = [
        {
          x: domain,
          y: counts,
          error_y: {
            type: "data",
            array: errors,
          },
          type: "bar",
          marker: {
            color: colors.color_scale_gray_5,
          },
          name: `${this.refData.name}@${this.refData.version}`,
        },
        {
          x: alternativeADomain,
          y: alternativeACounts,
          error_y: {
            type: "data",
            array: alternativeAErrors,
          },
          type: "bar",
          marker: {
            color: colors.color_scale_blue_5,
          },
          name: `${this.alternativeA.name}@${this.alternativeA.version}`,
        },
      ];
      if (this.alternativeB) {
        let alternativeBDomain = Object.keys(
          this.alternativeBStats.frequencies
        );
        let alternativeBCounts = Object.values(
          this.alternativeBStats.frequencies
        );
        let alternativeBErrors = [];
        for (const [key, value] of Object.entries(
          this.alternativeBStats.frequencies_lb
        )) {
          alternativeBErrors.push(
            this.alternativeBStats.frequencies[key] - value
          );
        }
        plots.push({
          x: alternativeBDomain,
          y: alternativeBCounts,
          error_y: {
            type: "data",
            array: alternativeBErrors,
          },
          type: "bar",
          marker: {
            color: colors.color_scale_red_5,
          },
          name: `${this.alternativeB.name}@${this.alternativeB.version}`,
        });
      }

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
