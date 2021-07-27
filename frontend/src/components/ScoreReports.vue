<template>
  <div class="schemaView mb-4 d-flex flex-row">
    <div
      v-for="(scoreData, scoreName) in refDef.scores"
      :key="scoreName"
      class="m-1"
    >
      <Gauge
        :data="scoreData"
        :alternativeA="getScore(alternativeA, scoreName)"
        :alternativeB="getScore(alternativeB, scoreName)"
      />
    </div>
  </div>

</template>

<script>
const octicons = require("@primer/octicons");
const PPP = 10; // Plots per page
import Gauge from "@/components/Gauge.vue";
export default {
  props: ["refDef", "alternativeA", "alternativeB"],
  components: { Gauge },
  data: function () {
    return {
      octicons,
    };
  },
  methods: {
    getScore(data, scoreName) {
      if (data) {
        return data.scores[scoreName];
      } else {
        return undefined;
      }
    },
  },
  computed: {
    profileReducers() {
      return this.refDef.reducers;
    },
  },
  watch: {},
};
</script>

<style lang="scss">
ul.noBullets {
  list-style-type: none; /* Remove bullets */
}
</style>
