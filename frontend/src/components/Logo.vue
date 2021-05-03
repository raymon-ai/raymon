<template>
  <div class="logo">
    <img
      class="logo-asset"
      :src="logo"
    />
  </div>
</template>

<script>
export default {
  name: "Logo",
  components: {},
  data: function () {
    return {
      logo: require("@/assets/logo-blue.png"),

      // alltraces: [],
    };
  },
};
</script>

<style scoped>
.logo-asset {
  width: 100%;
  height: 100%;
}
.logo {
  width: 60px;
  height: 70px;
}
</style>
