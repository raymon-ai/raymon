<template>

  <ViewSchema
    :profile="profileLoaded"
    :poi="poiLoaded"
  />

</template>

<script>
import ViewSchema from "@/ViewSchema.vue";

export default {
  name: "SchemaViewStr",
  props: ["profile", "poi"],
  components: {
    ViewSchema,
  },
  data() {
    return {};
  },
  methods: {},
  computed: {
    profileLoaded() {
      const loaded = JSON.parse(this.profile);
      return loaded;
    },
    poiLoaded() {
      return JSON.parse(this.poi);
    },
  },
};
</script>

<style lang="scss">
@import "@primer/css/index.scss";
@import "plotly.js/src/css/style.scss";
</style>
