<template>

  <body>
    <div
      id="app"
      class="mainWindow m-2 p-2 white"
    >
      <Header
        :schemaDef="schemaLoaded"
        :otherDef="otherLoaded"
        @setPage="setPage"
      />
      <ComponentTypeNav
        v-if="showNav"
        :types="Object.keys(componentTypes)"
        @componentType="updateComponentType"
      />
      <component
        :is="pageToShow"
        :schemaDef="schemaLoaded"
        :otherDef="otherLoaded"
        :compareStats="compareLoaded"
        :featureName="featureName"
        :componentType="componentPage"
        @setPage="setPage"
      />
    </div>
  </body>
</template>

<script>
import Header from "@/components/Header.vue";
import ComponentTypeNav from "@/components/ComponentTypeNav.vue";

import FeatureOverview from "@/components/compare/FeatureOverview.vue";
import FeatureDetailView from "@/components/compare/FeatureDetailView.vue";
export default {
  name: "SchemaCompare",
  props: ["comparison"],
  components: {
    Header,
    FeatureDetailView,
    FeatureOverview,
    ComponentTypeNav,
  },
  data() {
    return {
      featureName: undefined,
      componentTypes: {
        Inputs: "input_components",
        Outputs: "output_components",
        Actuals: "actual_components",
        Scores: "score_components",
      },
      componentPage: "input_components",
    };
  },
  methods: {
    setPage(page) {
      console.log("setting page to: ", page);
      this.featureName = page;
    },
    updateComponentType(type) {
      this.componentPage = this.componentTypes[type];
    },
  },
  computed: {
    loadedJSON() {
      return JSON.parse(this.comparison);
    },
    schemaLoaded() {
      return this.loadedJSON.reference;
    },
    otherLoaded() {
      return this.loadedJSON.other;
    },
    compareLoaded() {
      return this.loadedJSON.report;
    },
    pageToShow() {
      if (this.featureName !== undefined) {
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
  max-width: 1000px;
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
