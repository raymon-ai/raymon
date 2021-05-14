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
      console.log("Loaded JSON: ", loaded);

      return loaded;
    },
    poiLoaded() {
      return JSON.parse(this.poi);
    },
  },
};
</script>

<style lang="scss">
</style>
