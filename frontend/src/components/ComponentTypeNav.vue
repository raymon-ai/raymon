<template>

  <nav
    class="UnderlineNav mt-2"
    aria-label="Foo bar"
  >
    <div class="UnderlineNav-body">

      <a
        v-for="type in pages"
        :key="type"
        class="UnderlineNav-item"
        href="#url"
        :aria-current="type==selectedType"
        @click="selectPage(type)"
      >{{type}}</a>

    </div>
  </nav>

</template>

<script>
export default {
  name: "TypeNav",
  components: {},
  data() {
    return {
      selectedType: "Inputs",
      pages: ["Inputs", "Outputs", "Actuals", "Evaluations", "Scores"],
    };
  },
  methods: {
    selectPage(type) {
      this.selectedType = type;
      this.$emit("viewComponentPage", type);
    },
  },
  computed: {},
};
</script>

<style lang="scss">
</style>
