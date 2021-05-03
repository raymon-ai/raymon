<template>
  <span>
    <span
      v-html="octicons['arrow-down'].toSVG()"
      class="icon"
      :class="{'active': isActive('down'), 'inActive': !isActive('down')}"
      @click="setActiveSort('down')"
    />
    <span
      v-html="
                octicons['arrow-up'].toSVG()"
      class="icon"
      :class="{'active': isActive('up'), 'inActive': !isActive('up')}"
      @click="setActiveSort('up')"
    />
  </span>

</template>

<script>
const octicons = require("@primer/octicons");
const PPP = 10; // Plots per page
export default {
  props: ["field", "active"],

  data: function () {
    return { octicons };
  },
  methods: {
    isActive(direction) {
      return (
        this.field === this.active.activeSortField &&
        direction === this.active.activeSortDirection
      );
    },
    setActiveSort(direction) {
      this.$emit("activeSortChanged", {
        activeSortField: this.field,
        activeSortDirection: direction,
      });
    },
  },
};
</script>

<style lang="scss">
.icon {
  width: 16px;
  height: 16px;
}
.active {
  color: #6a737d;
}
.inActive {
  color: #e1e4e8;
}
</style>
