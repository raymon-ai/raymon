<template>

  <nav
    class="UnderlineNav mt-2"
    aria-label="Foo bar"
  >
    <div class="UnderlineNav-body">

      <a
        v-for="type in types"
        :key="type"
        class="UnderlineNav-item"
        href="#url"
        :aria-current="type==selectedType"
        @click="selectType(type)"
      >{{type}}</a>

    </div>
  </nav>

</template>

<script>
export default {
  name: "SchemaView",
  props: ["types"],
  components: {},
  data() {
    return {
      selectedType: this.types[0],
    };
  },
  methods: {
    selectType(type) {
      this.selectedType = type;
      this.$emit("componentType", type);
    },
  },
  computed: {},
};
</script>

<style lang="scss">
</style>
