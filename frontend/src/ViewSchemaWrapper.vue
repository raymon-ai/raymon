<template>
  <ViewSchemaStr
    :profile="refDefComputed"
    :poi="poiComputed"
  />
</template>

<script>
import schemaFromJson from "@/assets/cheap-houses@0.0.1.json";
import ViewSchemaStr from "@/ViewSchemaStr.vue";
export default {
  name: "ViewSchemaWrapper",
  data() {
    return {};
  },
  components: {
    ViewSchemaStr,
  },
  computed: {
    refDefComputed() {
      // this is to load data for testing
      let refDef = undefined;

      refDef = schemaFromJson;
      console.log("Loading schema from json.");
      return JSON.stringify(refDef);
    },
    poiComputed() {
      return JSON.stringify({
        "1stflrsf": 2000,
        alley: "Grvl",
      });
    },
  },
};
</script>

<style lang="scss">
@import "@primer/css/index.scss";
@import "plotly.js/src/css/style.scss";
</style>
