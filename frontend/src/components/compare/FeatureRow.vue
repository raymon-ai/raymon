
<template>
  <tr class="tableRayContentRow tableRayContentRow">

    <td class="p-1">
      <a
        href="#"
        @click="goToDetailView"
      >{{ componentName }}</a>

    </td>
    <td class="px-2 codeLikeContent">
      {{ componentDataType }}
    </td>

    <td class="px-2 codeLikeContent pvalueColumn">
      <p
        class="f3"
        :class="{'orange': isDrift, 'green': !isDrift}"
      > {{driftStr}}</p>
      <!-- <span :class="{'Label mr-1 Label--red': isDrift, 'Label mr-1 Label--green': !isDrift}">
        {{reportData.drift.drift.toFixed(2)}}
      </span> -->
    </td>
    <!-- <td class="px-2 codeLikeContent">
      {{reportData.impact.toFixed(2)}}

    </td> -->
    <td class="px-2">
      <div class="d-flex flex-column flex-items-begin">
        <p>
          <span
            class="f6"
            :class="leftColorClass"
          >{{this.leftStats.invalids.toFixed(2)}}</span>
          <span
            v-html="octicons['arrow-right'].toSVG()"
            class="mx-1"
          ></span>
          <span
            class="f6"
            :class="rightColorClass"
          > {{this.rightStats.invalids.toFixed(2)}}</span>
        </p>
        <p
          class="f4"
          :class="{'orange': isPinvAlert, 'green': !isPinvAlert}"
        >
          {{invalidsDiffStr}}
        </p>
      </div>

    </td>
    <td class="px-2">
      <div
        v-if="'mean' in refStats"
        class="d-flex flex-column flex-items-begin"
      >
        <p>
          <span
            class="f6"
            :class="leftColorClass"
          >{{this.leftStats.mean.toExponential(2)}}</span>
          <span
            v-html="octicons['arrow-right'].toSVG()"
            class="mx-1"
          ></span>
          <span
            class="f6"
            :class="rightColorClass"
          > {{this.rightStats.mean.toExponential(2)}}</span>
        </p>
        <p
          class="f4"
          :class="{'orange': isMeanAlert, 'green': !isMeanAlert}"
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
import { colors } from "@/js/colors.js";
export default {
  components: { VuePlotly },
  props: [
    "refComponentData",
    "alternativeAComponentData",
    "alternativeBComponentData",
    "reportData",
  ],
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
    refStats() {
      return this.refComponentData.state.stats.state;
    },
    alternativeAStats() {
      return this.alternativeAComponentData.state.stats.state;
    },
    alternativeBStats() {
      return this.alternativeBComponentData.state.stats.state;
    },
    isNumeric() {
      return (
        this.componentDataType.toLowerCase() === "int" ||
        this.componentDataType.toLowerCase() === "float"
      );
    },
    driftStr() {
      return `${Math.trunc(this.reportData.drift.drift * 100)}%`;
    },
    invalidsDiffStr() {
      return `${Math.trunc(this.reportData.invalids.invalids * 100)}%`;
    },
    meanDiffStr() {
      return `${Math.trunc(this.reportData.mean.mean * 100)}%`;
    },
    thisMeanNice() {
      return this.refStats.mean.toExponential(2);
    },
    alternativeAMeanNice() {
      return this.alternativeAStats.mean.toExponential(2);
    },
    componentName() {
      return this.refComponentData.state.name;
    },
    componentDataType() {
      return this.refComponentData.state.dtype.toLowerCase();
    },
    isDrift() {
      return this.reportData.drift.alert;
    },
    isPinvAlert() {
      return this.reportData.invalids.alert;
    },
    isMeanAlert() {
      return this.reportData.mean.alert;
    },
    leftStats() {
      if (this.alternativeBComponentData) {
        return this.alternativeAStats;
      } else {
        return this.refStats;
      }
    },
    rightStats() {
      if (this.alternativeBComponentData) {
        return this.alternativeBStats;
      } else {
        return this.alternativeAStats;
      }
    },
    leftColorClass() {
      if (this.alternativeBComponentData) {
        return "blue";
      } else {
        return "gray";
      }
    },
    rightColorClass() {
      if (this.alternativeBComponentData) {
        return "red";
      } else {
        return "blue";
      }
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
          x: this.refStats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: colors.color_scale_gray_5,
          },
        },
        {
          x: this.alternativeAStats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: colors.color_scale_blue_5,
          },
        },
      ];
      if (this.alternativeBComponentData) {
        plots.push({
          x: this.alternativeBStats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: colors.color_scale_red_5,
          },
        });
      }
      return plots;
    },
    getCategoricPlotData() {
      let domain = Object.keys(this.refStats.frequencies);
      let counts = Object.values(this.refStats.frequencies);

      let alternativeADomain = Object.keys(this.alternativeAStats.frequencies);
      let alternativeACounts = Object.values(
        this.alternativeAStats.frequencies
      );

      let plots = [
        {
          x: domain,
          y: counts,
          type: "bar",
          marker: {
            color: colors.color_scale_gray_5,
          },
        },
        {
          x: alternativeADomain,
          y: alternativeACounts,
          type: "bar",
          marker: {
            color: colors.color_scale_blue_5,
          },
        },
      ];
      if (this.alternativeBComponentData) {
        let alternativeBDomain = Object.keys(
          this.alternativeBStats.frequencies
        );
        let alternativeBCounts = Object.values(
          this.alternativeBStats.frequencies
        );
        plots.push({
          x: alternativeBDomain,
          y: alternativeBCounts,
          type: "bar",
          marker: {
            color: colors.color_scale_red_5,
          },
        });
      }
      return plots;
    },
  },
};
</script>

<style lang="scss">
@import "@primer/css/index.scss";
.gray {
  color: var(--color-scale-gray-5);
}
.red {
  color: var(--color-scale-red-5);
}
.orange {
  color: var(--color-scale-orange-5);
}
.blue {
  color: var(--color-scale-blue-5);
}
.green {
  color: var(--color-scale-green-5);
}
</style>