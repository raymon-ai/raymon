<template>

  <div class="d-inline-flex">
    <div
      id="app"
      class="mainWindow m-2 p-2 white"
    >
      <Header
        :refDef="refData"
        :alternativeA="alternativeA"
        :alternativeB="alternativeB"
        @setPage="setPage"
      />
      <ScoreReports
        :refDef="refData"
        :alternativeA="alternativeA"
        :alternativeB="alternativeB"
      />

      <ComponentTypeNav
        v-if="showNav"
        @viewComponentPage="updateComponentView"
      />
      <component
        :is="pageToShow"
        :refData="refData"
        :alternativeA="alternativeA"
        :alternativeB="alternativeB"
        :reportData="reportData"
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

import FeatureOverview from "@/components/compare/FeatureOverview.vue";
import FeatureDetailView from "@/components/compare/FeatureDetailView.vue";
import ScoreReports from "@/components/ScoreReports.vue";

export default {
  name: "CompareSchema",
  props: ["comparison"],
  components: {
    Header,
    FeatureDetailView,
    FeatureOverview,
    ComponentTypeNav,
    ScoreReports,
  },
  data() {
    return {
      componentName: undefined,
      componentPage: "Inputs",
    };
  },
  methods: {
    setPage(page) {
      this.componentName = page;
    },
    updateComponentView(type) {
      this.componentPage = type;
    },
  },
  computed: {
    refData() {
      return this.comparison.reference;
    },
    alternativeA() {
      return this.comparison.alternativeA;
    },
    alternativeB() {
      return this.comparison.alternativeB;
    },
    reportData() {
      return this.comparison.component_reports;
    },

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
