<template>

  <body>

    <div
      id="app"
      class="mainWindow m-2 p-2 white"
    >
      <Header
        :schemaDef="schemaLoaded"
        :poi="poiLoaded"
        @setPage="setPage"
      />
      <component
        :is="pageToShow"
        :schemaDef="schemaLoaded"
        :poi="poiLoaded"
        :featureName="featureName"
        @setPage="setPage"
      />

    </div>
  </body>

</template>

<script>
import Header from "@/components/Header.vue";
import FeatureOverview from "@/components/compare/FeatureOverview.vue";
import FeatureDetailView from "@/components/compare/FeatureDetailView.vue";
export default {
  name: "SchemaView",
  props: ["schema", "poi"],
  components: {
    Header,
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
    schemaLoaded() {
      return JSON.parse(this.schema);
    },
    poiLoaded() {
      return JSON.parse(this.poi);
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
