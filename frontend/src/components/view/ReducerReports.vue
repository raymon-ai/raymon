<template>
  <div class="schemaView mb-4">
    <!-- <h3 class="h3">
      Reducer Values:
    </h3>
    <div
      v-for="(reducer, name) in profileReducers"
      :key="name"
    >
      <h4 class="h4">
        {{name}}:
      </h4>
      <ul class="noBullets">
        <li
          v-for="result, tag in reducer.state.results"
          :key="tag"
        > <strong>{{tag}}:</strong> {{result.toFixed(2)}} </li>
      </ul>
    </div> -->
  </div>

</template>

<script>
const octicons = require("@primer/octicons");
const PPP = 10; // Plots per page
export default {
  props: ["refDef", "poi", "componentType"],
  components: {},
  data: function () {
    return {
      octicons,
    };
  },
  methods: {},
  computed: {
    profileReducers() {
      return this.refDef.reducers;
    },
  },
  watch: {},
};
</script>

<style lang="scss">
ul.noBullets {
  list-style-type: none; /* Remove bullets */
}
</style>
