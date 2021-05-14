<template>
  <div class="logo">
    <img
      class="logo-asset"
      src="./../../public/logo-blue.png"
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
  width: 60px;
  height: 70px;
}
.logo {
  width: 60px;
  height: 70px;
}
</style>
