
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
    <!-- <td class="px-2 codeLikeContent">
      {{ componentImportance }}
    </td> -->
    <td class="px-2 codeLikeContent">
      {{min}}
    </td>
    <td class="px-2 codeLikeContent">
      {{max}}

    </td>
    <td class="px-2 codeLikeContent">
      {{invalids}}

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
  props: ["componentData", "poi"],
  data: function () {
    return {
      plotLayout: {
        autosize: false,
        width: 300,
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
      return this.componentData.state.stats.state;
    },
    isNumeric() {
      return (
        this.componentDataType.toLowerCase() === "int" ||
        this.componentDataType.toLowerCase() === "float"
      );
    },
    min() {
      if (this.isNumeric) {
        return this.stats.min;
      } else {
        return "NA";
      }
    },
    max() {
      if (this.isNumeric) {
        return this.stats.max;
      } else {
        return "NA";
      }
    },
    invalids() {
      return this.stats.invalids.toFixed(2);
    },
    componentName() {
      return this.componentData.state.name;
    },
    componentDataType() {
      return this.componentData.state.dtype.toLowerCase();
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
    goToDetailView() {
      this.$parent.$emit("setPage", this.componentName);
    },
    getNumberPlotData() {
      let plots = [
        {
          x: this.stats.percentiles_lb.concat(
            this.stats.percentiles_ub.slice().reverse()
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
          x: this.stats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: colors.color_scale_blue_5,
          },
        },
      ];
      if (this.poi) {
        plots.push({
          x: [this.poi, this.poi],
          y: [0, 100],
          mode: "lines",
          line: {
            color: colors.color_scale_green_5,
            width: 1.5,
          },
        });
      }
      return plots;
    },
    getCategoricPlotData() {
      let domain = Object.keys(this.stats.frequencies);
      let counts = Object.values(this.stats.frequencies);
      let errors = [];
      for (const [key, value] of Object.entries(this.stats.frequencies_lb)) {
        errors.push(this.stats.frequencies[key] - value);
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
            color: colors.color_scale_blue_5,
          },
        },
      ];
      if (this.poi) {
        plots.push({
          x: [this.poi, this.poi],
          y: [0, Math.max(...counts)],
          mode: "lines",
          line: {
            color: colors.color_scale_green_5,
            width: 1.5,
          },
        });
      }
      return plots;
    },
  },
};
</script>

<style>
</style>