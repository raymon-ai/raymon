
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
import { red, green, blue, yellow } from "@/colors.js";
export default {
  components: { VuePlotly },
  props: ["componentData", "poi"],
  data: function () {
    return {
      plotLayout: {
        autosize: false,
        width: 400,
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
    isNumeric() {
      return (
        this.componentType.toLowerCase() === "int" ||
        this.componentType.toLowerCase() === "float"
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
      return this.componentData.component.name;
    },
    componentType() {
      const splits = this.componentData.component_class.split(".");
      return splits.slice(-1)[0].replace("Component", "");
    },
    componentImportance() {
      return this.componentData.component.importance;
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
          x: this.stats.percentiles,
          y: [...Array(101).keys()],
          type: "scatter",
          marker: {
            color: blue,
          },
        },
      ];
      if (this.poi) {
        plots.push({
          x: [this.poi, this.poi],
          y: [0, 100],
          mode: "lines",
          line: {
            color: yellow,
            width: 1.5,
          },
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
            color: blue,
          },
        },
      ];
      if (this.poi) {
        plots.push({
          x: [this.poi, this.poi],
          y: [0, Math.max(...counts)],
          mode: "lines",
          line: {
            color: yellow,
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