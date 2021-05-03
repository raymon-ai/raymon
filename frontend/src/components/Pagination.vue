<template>
  <div
    class="paginate-container"
    aria-label="Pagination"
  >
    <div class="pagination">
      <span
        class="previous_page"
        :aria-disabled="canNotDecrease"
        @click="decreasePage"
      >Previous</span>
      Page {{ page + 1 }} of {{ nPages }}
      <span
        class="next_page"
        :aria-disabled="canNotIncrease"
        @click="increasePage"
      >Next</span>
    </div>
  </div>
</template>

<script>
export default {
  name: "Pagination",
  props: ["elements", "ppp", "page"],
  components: {},
  data: function () {
    return {
      // alltraces: [],
      featureFilter: "",
    };
  },
  methods: {
    increasePage() {
      if (this.canNotIncrease) {
        return;
      } else {
        this.$emit("pagechanged", this.page + 1);
      }
    },
    decreasePage() {
      if (this.canNotDecrease) {
        return;
      } else {
        this.$emit("pagechanged", this.page - 1);
      }
    },
  },
  computed: {
    canNotDecrease() {
      return this.page === 0;
    },
    canNotIncrease() {
      return this.page >= this.nPages - 1;
    },
    nPages() {
      return Math.ceil(Object.keys(this.elements).length / this.ppp);
    },
  },
  mounted() {},
};
</script>

<style>
</style>
