<template>
  <div class="schemaView mt-3">
    <h1> Feature: <span class="codeLike">{{featureName}} </span> </h1>
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

            <th class="raytablehead typeColumn px-2">
              <label>{{schemaDef.name}}@{{schemaDef.version}} </label>

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
      >Back</a>
    </div>
  </div>
</template>


<script>
const octicons = require("@primer/octicons");
import VuePlotly from "@statnett/vue-plotly";
import { red, green, blue, yellow } from "@/schemaFrontend/colors.js";
export default {
  components: { VuePlotly },
  props: ["schemaDef", "poi", "featureName"],
  data: function () {
    return {
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
          title: this.featureName,
        },
        yaxis: {
          title: "cdf",
        },
      };
    },
    featureData() {
      return this.schemaDef.features[this.featureName];
    },
    featureType() {
      const splits = this.featureData.feature_class.split(".");
      return splits.slice(-1)[0];
    },
    poiValue() {
      return this.poi[this.featureName];
    },
    stats() {
      return this.featureData.feature.stats;
    },
    isNumeric() {
      return (
        this.featureType.toLowerCase() === "intfeature" ||
        this.featureType.toLowerCase() === "floatfeature"
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
        return Object.keys(this.stats.domain_counts);
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

    getNumberPlotData() {
      let plots = [
        {
          x: this.stats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: blue,
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
            color: yellow,
            width: 1.5,
          },
          name: "poi",
        });
      }
      return plots;
    },
    getCategoricPlotData() {
      let domain = Object.keys(this.stats.domain_counts);
      let counts = Object.values(this.stats.domain_counts);

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
      ];
      if (this.poiValue) {
        plots.push({
          x: [this.poiValue, this.poiValue],
          y: [0, Math.max(...counts)],
          mode: "lines",
          line: {
            color: yellow,
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
