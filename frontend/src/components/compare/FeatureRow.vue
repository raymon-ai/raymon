
<template>
  <tr class="tableRayContentRow tableRayContentRow">

    <td class="p-1">
      <a
        href="#"
        @click="goToDetailView"
      >{{ componentName }}</a>

    </td>
    <td class="px-2 codeLikeContent">
      {{ componentType }}
    </td>

    <td class="px-2 codeLikeContent pvalueColumn">
      <p
        class="f3"
        :class="{'red': isDrift, 'green': !isDrift}"
      > {{driftStr}}</p>
      <!-- <span :class="{'Label mr-1 Label--red': isDrift, 'Label mr-1 Label--green': !isDrift}">
        {{compareStats.drift.drift.toFixed(2)}}
      </span> -->
    </td>
    <!-- <td class="px-2 codeLikeContent">
      {{compareStats.impact.toFixed(2)}}

    </td> -->
    <td class="px-2">
      <div class="d-flex flex-column flex-items-begin">
        <p>
          <span class="blue f6">{{this.stats.invalids.toFixed(2)}}</span>
          <span
            v-html="octicons['arrow-right'].toSVG()"
            class="mx-1"
          ></span>
          <span class="red f6"> {{this.otherStats.invalids.toFixed(2)}}</span>
        </p>
        <p
          class="f4"
          :class="{'red': isPinvAlert, 'green': !isPinvAlert}"
        >
          {{invalidsDiffStr}}
        </p>
      </div>

    </td>
    <td class="px-2">
      <div
        v-if="'mean' in stats"
        class="d-flex flex-column flex-items-begin"
      >
        <p>
          <span class="blue f6">{{thisMeanNice}}</span>
          <span
            v-html="octicons['arrow-right'].toSVG()"
            class="mx-1"
          ></span>
          <span class="red f6"> {{otherMeanNice}}</span>
        </p>
        <p
          class="f4"
          :class="{'red': isMeanAlert, 'green': !isMeanAlert}"
        >
          {{meanDiffStr}}
        </p>
      </div>
      <div v-else> - </div>

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
  props: ["componentData", "otherFeatureData", "compareStats"],
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
      return this.componentData.component.stats;
    },
    otherStats() {
      return this.otherFeatureData.component.stats;
    },
    isNumeric() {
      return (
        this.componentType.toLowerCase() === "int" ||
        this.componentType.toLowerCase() === "float"
      );
    },
    driftStr() {
      return `${Math.trunc(this.compareStats.drift.drift * 100)}%`;
    },
    invalidsDiff() {
      let diff = this.otherStats.invalids - this.stats.invalids;
      return diff;
    },
    invalidsDiffStr() {
      return `${Math.trunc(this.compareStats.invalids.invalids * 100)}%`;
    },
    meanDiffStr() {
      return `${Math.trunc(this.compareStats.mean.mean * 100)}%`;
    },
    thisMeanNice() {
      return this.stats.mean.toExponential(2);
    },
    otherMeanNice() {
      return this.otherStats.mean.toExponential(2);
    },
    componentName() {
      return this.componentData.component.name;
    },
    componentType() {
      const splits = this.componentData.component_class.split(".");
      return splits.slice(-1)[0].replace("Component", "");
    },
    componentImportance() {
      return this.componentData.component.importance;
    },
    isDrift() {
      return this.compareStats.drift.alert;
    },
    isPinvAlert() {
      return this.compareStats.invalids.alert;
    },
    isMeanAlert() {
      return this.compareStats.mean.alert;
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
      this.$parent.$emit("setPage", this.componentName);
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
@import "@primer/css/index.scss";

.red {
  color: #d73a49;
}
.blue {
  color: #0366d6;
}
.green {
  color: #28a745;
}
</style>