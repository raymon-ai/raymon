<template>
  <div class="figContainer">
    <div class="d-flex flex-column flex-items-center mx-3">
      <div
        class="f2"
        :class="[leftColorClass]"
      >
        {{ leftValue }}
      </div>
      <div class="f5 color-text-secondary">{{ name }}</div>
      <div
        v-if="alternativeA"
        class="f2"
        :class="[rightColorClass]"
      >
        {{ rightValue }}
      </div>
    </div>

  </div>
</template>

<script>
var octicons = require("@primer/octicons");

export default {
  name: "Gauge",
  components: {},
  props: ["data", "alternativeA", "alternativeB"],
  data: function () {
    return {
      // alltraces: [],
      gauges: {},
      secondaryGauges: {},
      loaded: false,
    };
  },
  methods: {
    extractGaugeData(data) {
      delete data.bucket;
      let cleaned = {};
      for (let key of Object.keys(data)) {
        cleaned[key] = Math.round(data[key][0] * 100) / 100;
      }
      return cleaned;
    },
  },
  mounted() {},
  computed: {
    name() {
      return this.data.state.name;
    },

    leftStats() {
      if (this.alternativeB) {
        return this.alternativeA;
      } else {
        return this.data;
      }
    },
    rightStats() {
      if (this.alternativeB) {
        return this.alternativeB;
      } else {
        return this.alternativeA;
      }
    },
    leftColorClass() {
      if (this.alternativeB) {
        return "blue";
      } else {
        return "gray";
      }
    },
    rightColorClass() {
      if (this.alternativeB) {
        return "red";
      } else {
        return "blue";
      }
    },
    leftValue() {
      return this.leftStats.state.result.toFixed(2);
    },
    rightValue() {
      return this.rightStats.state.result.toFixed(2);
    },
  },
  watch: {},
};
</script>

<style lang="scss" scoped>
.referenceGauge {
  color: var(--color-scale-gray-7);
}
.primaryGauge {
  color: var(--color-scale-blue-5);
}
.secondaryGauge {
  color: var(--color-scale-red-5);
}

.figContainer {
  width: 100%;
  height: 100%;
  padding: 10px;
  display: flex;
  flex-direction: column;
  position: relative;
  border: 1px solid #f6f8fa;
  background-color: #ffffff;
  box-shadow: 1px 1px 1px 1px rgba(27, 31, 35, 0.04) !important;
  /* overflow: hidden; */
}
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
