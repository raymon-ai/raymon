<template>

  <CompareSchema :comparison="loadedJSON" />
</template>

<script>
import CompareSchema from "@/CompareSchema.vue";

export default {
  name: "SchemaCompareStr",
  props: ["comparison"],
  components: {
    CompareSchema,
  },
  data() {
    return {};
  },
  methods: {},
  computed: {
    loadedJSON() {
      const loaded = JSON.parse(this.comparison);
      console.log("Loaded JSON: ", loaded);
      return loaded;
    },
  },
};
</script>

<style lang="scss">
</style>
