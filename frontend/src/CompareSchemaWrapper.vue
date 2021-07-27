<template>
  <CompareSchemaStr :comparison="comparisonComputed" />
</template>

<script>
import compareDefFromJson from "@/assets/housepricescheap@3.0.0vshousepricesexpensive@3.0.0.json";
// import compareDefFromJson from "@/assets/contrast_missing.json";
import CompareSchemaStr from "@/CompareSchemaStr.vue";
export default {
  name: "CompareSchemaWrapper",
  data() {
    return {};
  },
  components: {
    CompareSchemaStr,
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
