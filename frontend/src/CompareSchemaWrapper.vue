<template>
  <CompareSchema :comparison="comparisonComputed" />
</template>

<script>
import compareDefFromJson from "@/assets/contrast.json";
import CompareSchema from "@/CompareSchema.vue";
export default {
  name: "CompareSchemaWrapper",
  data() {
    return {};
  },
  components: {
    CompareSchema,
  },
  computed: {
    comparisonComputed() {
      // this is to load data for testing
      let compareDef = undefined;
      compareDef = compareDefFromJson;
      console.log("Loading schema from json.");

      return JSON.stringify(compareDef);
    },
  },
};
</script>

<style lang="scss">
// @import "@primer/css/index.scss";
// @import "plotly.js/src/css/style.scss";
</style>
