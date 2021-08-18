
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
    </td>

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
      try {
        return this.alternativeAComponentData.state.stats.state;
      } catch (error) {
        return undefined;
      }
    },
    alternativeBStats() {
      try {
        return this.alternativeBComponentData.state.stats.state;
      } catch (error) {
        return undefined;
      }
    },
    isValid() {
      return typeof this.reportData !== "undefined";
    },
    isNumeric() {
      return (
        this.componentDataType.toLowerCase() === "int" ||
        this.componentDataType.toLowerCase() === "float"
      );
    },
    driftStr() {
      if (this.isValid) {
        return `${Math.trunc(this.reportData.drift.drift * 100)}%`;
      } else {
        return "None";
      }
    },
    invalidsDiffStr() {
      if (this.isValid) {
        return `${Math.trunc(this.reportData.invalids.invalids * 100)}%`;
      } else {
        return "None";
      }
    },

    componentName() {
      return this.refComponentData.state.name;
    },
    componentDataType() {
      return this.refComponentData.state.dtype.toLowerCase();
    },
    isDrift() {
      if (this.isValid) {
        return this.reportData.drift.alert;
      } else {
        return false;
      }
    },
    isPinvAlert() {
      if (this.isValid) {
        return this.reportData.invalids.alert;
      } else {
        return false;
      }
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
          x: this.refStats.percentiles_lb.concat(
            this.refStats.percentiles_ub.slice().reverse()
          ),
          y: Array.from(Array(101).keys()).concat(
            Array.from(Array(101).keys()).reverse()
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
        },
      ];
      if (this.alternativeAComponentData) {
        plots.push(
          {
            x: this.alternativeAStats.percentiles_lb.concat(
              this.alternativeAStats.percentiles_ub.slice().reverse()
            ),
            y: Array.from(Array(101).keys()).concat(
              Array.from(Array(101).keys()).reverse()
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
          }
        );
      }

      if (this.alternativeBComponentData) {
        plots.push(
          {
            x: this.alternativeBStats.percentiles_lb.concat(
              this.alternativeBStats.percentiles_ub.slice().reverse()
            ),
            y: Array.from(Array(101).keys()).concat(
              Array.from(Array(101).keys()).reverse()
            ),
            fill: "toself",
            fillcolor: "rgba(215, 58, 73, 0.2)", // same red, but lower opacity
            line: {
              color: "transparent",
            },
            hoverinfo: "skip",
            showlegend: false,
          },
          {
            x: this.alternativeBStats.percentiles,
            y: [...Array(101).keys()],
            type: "scatter",
            marker: {
              color: colors.color_scale_red_5,
            },
          }
        );
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
        },
      ];
      if (this.alternativeBComponentData) {
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