<template>

  <CompareSchema :comparison="loadedJSON" />
</template>

<script>
import CompareSchema from "@/CompareSchema.vue";

export default {
  name: "SchemaCompareStrJSON",
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
      return JSON.parse(this.comparison);
    },
  },
};
</script>

<style lang="scss">
</style>
