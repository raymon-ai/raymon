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
      <component
        :is="pageToShow"
        :schemaDef="schemaLoaded"
        :otherDef="otherLoaded"
        :compareStats="compareStatsLoaded"
        :featureName="featureName"
        @setPage="setPage"
      />
    </div>
  </body>
</template>

<script>
import Header from "@/schemaFrontend/components/Header.vue";
import FeatureOverview from "@/schemaFrontend/components/compare/FeatureOverview.vue";
import FeatureDetailView from "@/schemaFrontend/components/compare/FeatureDetailView.vue";
// import store from "./store";
export default {
  name: "SchemaCompare",
  props: ["comparison"],
  components: {
    Header,
    FeatureDetailView,
    FeatureOverview,
  },
  data() {
    return {
      featureName: undefined,
    };
  },
  methods: {
    setPage(page) {
      console.log("setting page to: ", page);
      this.featureName = page;
    },
  },
  computed: {
    loadedJSON() {
      return JSON.parse(this.comparison);
    },
    schemaLoaded() {
      return this.loadedJSON.self;
    },
    otherLoaded() {
      return this.loadedJSON.other;
    },
    compareStatsLoaded() {
      return this.loadedJSON.feature_drift;
    },
    pageToShow() {
      if (this.featureName !== undefined) {
        return FeatureDetailView;
      } else {
        return FeatureOverview;
      }
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
