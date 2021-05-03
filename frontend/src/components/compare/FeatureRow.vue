
<template>
  <tr class="tableRayContentRow tableRayContentRow">

    <td class="p-1">
      <a
        href="#"
        @click="goToDetailView"
      >{{ featureName }}</a>

    </td>
    <td class="px-2 codeLikeContent">
      {{ featureType }}
    </td>

    <td class="px-2 codeLikeContent pvalueColumn">
      <span :class="{'Label mr-1 Label--red': isDrift, 'Label mr-1 Label--green': !isDrift}">
        {{compareStats.drift.drift.toFixed(2)}}
      </span>
    </td>
    <!-- <td class="px-2 codeLikeContent">
      {{compareStats.impact.toFixed(2)}}

    </td> -->
    <td class="px-2">
      <div class="d-flex flex-column flex-items-center">
        <p>
          <span class="blue f6">{{this.stats.pinv.toFixed(2)}}</span>
          <span
            v-html="octicons['arrow-right'].toSVG()"
            class="mx-1"
          ></span>
          <span class="red f6"> {{compareStats.integrity.integrity.toFixed(2)}}</span>
        </p>
        <p class="f4">
          {{pinvDiffStr}}
        </p>
      </div>

    </td>

    <td class="px-2">
      <VuePlotly
        :data="plotData"
        :layout="plotLayout"
        :autoResize="false"
        :options="plotOptions"
      />
    </td>
  </tr>
</template>

<script>
const octicons = require("@primer/octicons");
import VuePlotly from "@statnett/vue-plotly";
import { red, green, blue, yellow } from "@/colors.js";
export default {
  components: { VuePlotly },
  props: ["featureData", "otherFeatureData", "compareStats"],
  data: function () {
    return {
      plotLayout: {
        autosize: false,
        width: 350,
        height: 100,
        margin: {
          l: 20,
          r: 0,
          b: 20,
          t: 20,
          pad: 0,
        },
        showlegend: false,
      },
      plotOptions: {
        staticPlot: false,
        displayModeBar: false,
      },
    };
  },
  computed: {
    stats() {
      return this.featureData.feature.stats;
    },
    otherStats() {
      return this.otherFeatureData.feature.stats;
    },
    isNumeric() {
      return (
        this.featureType.toLowerCase() === "int" ||
        this.featureType.toLowerCase() === "float"
      );
    },
    pinvDiff() {
      let diff = this.otherStats.pinv - this.stats.pinv;
      return diff;
    },
    pinvDiffStr() {
      let diff = this.pinvDiff;
      let diffstr = null;
      if (diff >= 0) {
        diffstr = `+${diff.toFixed(2)}`;
      } else {
        diffstr = `${diff.toFixed(2)}`;
      }
      return diffstr;
    },
    featureName() {
      return this.featureData.feature.name;
    },
    featureType() {
      const splits = this.featureData.feature_class.split(".");
      return splits.slice(-1)[0].replace("Component", "");
    },
    featureImportance() {
      return this.featureData.feature.importance;
    },
    isDrift() {
      return this.compareStats.alert_drift === "True";
    },
    isNotDrift() {
      return !this.isDrift;
    },
    isPinvAlert() {
      return this.compareStats.alert_inv === "True";
    },
    plotData() {
      if (this.isNumeric) {
        return this.getNumberPlotData();
      } else {
        return this.getCategoricPlotData();
      }
    },
    octicons() {
      return octicons;
    },
  },
  methods: {
    goToDetailView() {
      this.$parent.$emit("setPage", this.featureName);
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
        },
        {
          x: this.otherStats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: red,
          },
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
.red {
  color: #d73a49;
}
.blue {
  color: #0366d6;
}
</style>