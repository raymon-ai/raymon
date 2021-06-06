<template>

  <div class="d-inline-flex">

    <div
      id="app"
      class="mainWindow m-2 p-2 white"
    >
      <Header
        :refDef="profile"
        :poi="poi"
        @setPage="setPage"
      />
      <ComponentTypeNav
        v-if="showNav"
        @viewComponentPage="updateComponentView"
      />
      <component
        :is="pageToShow"
        :refDef="profile"
        :poi="poi"
        :componentName="componentName"
        :componentType="componentPage"
        @setPage="setPage"
      />

    </div>
  </div>

</template>

<script>
import Header from "@/components/Header.vue";
import ComponentTypeNav from "@/components/ComponentTypeNav.vue";

import FeatureOverview from "@/components/view/FeatureOverview.vue";
import FeatureDetailView from "@/components/view/FeatureDetailView.vue";
export default {
  name: "SchemaView",
  props: ["profile", "poi"],
  components: {
    Header,
    ComponentTypeNav,
  },
  data() {
    return {
      componentName: undefined,
      componentPage: "Inputs",
    };
  },
  methods: {
    setPage(page) {
      console.log("setting page to: ", page);
      this.componentName = page;
    },
    updateComponentView(type) {
      this.componentPage = type;
    },
  },
  computed: {
    pageToShow() {
      if (this.componentName !== undefined) {
        return FeatureDetailView;
      } else {
        return FeatureOverview;
      }
    },
    showNav() {
      return this.pageToShow === FeatureOverview;
    },
  },
};
</script>

<style lang="scss">
@import "@primer/css/index.scss";
@import "plotly.js/src/css/style.scss";

.white {
  background-color: white;
}

.mainWindow {
  min-width: 1000px;
}

.codeLikeContent {
  font-family: Courier;
  font-size: 12px;
  /* border-bottom: 1px dotted #0366d6;  */
}
.codeLike {
  font-family: Courier;
}
</style>
