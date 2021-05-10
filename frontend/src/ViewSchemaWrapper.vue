<template>
  <ViewSchemaStrJSON
    :profile="schemaDefComputed"
    :poi="poiComputed"
  />
</template>

<script>
import schemaFromJson from "@/assets/HousePricesCheap@1.0.0.json";
import ViewSchemaStrJSON from "@/ViewSchemaStrJSON.vue";
export default {
  name: "ViewSchemaWrapper",
  data() {
    return {};
  },
  components: {
    ViewSchemaStrJSON,
  },
  computed: {
    schemaDefComputed() {
      // this is to load data for testing
      let schemaDef = undefined;

      schemaDef = schemaFromJson;
      console.log("Loading schema from json.");
      return JSON.stringify(schemaDef);
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
