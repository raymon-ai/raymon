<template>

  <ViewSchema
    :profile="profileLoaded"
    :poi="poiLoaded"
  />

</template>

<script>
import ViewSchema from "@/ViewSchema.vue";

export default {
  name: "SchemaViewStrJSON",
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
      return JSON.parse(this.profile);
    },
    poiLoaded() {
      return JSON.parse(this.poi);
    },
  },
};
</script>

<style lang="scss">
</style>
