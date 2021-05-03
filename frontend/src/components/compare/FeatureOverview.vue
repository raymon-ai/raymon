<template>
  <div class="schemaView">
    <div class="my-3">
      <dl class="form-group">
        <div class="form-group-header">
          <h3 class="Box-title">Search: </h3>
        </div>
        <input
          class="form-control"
          type="text"
          placeholder="type a feature name here..."
          id="featurefilter"
          v-model="featureFilter"
          @input="changePage(0)"
        />
      </dl>

    </div>

    <div class="tableWrapper hideScrollbar">
      <table>
        <thead>
          <tr>
            <th class="raytablehead nameColumn px-2">
              <label>Feature </label>
              <SortArrows
                field="name"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />

            </th>

            <th class="raytablehead typeColumn px-2">
              <label>Type </label>
              <SortArrows
                field="type"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />
            </th>
            <th class="raytablehead valueColumn px-2">
              <label>Drift </label>
              <SortArrows
                field="drift"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />

            </th>
            <!-- <th class="raytablehead valueColumn px-2">
              <label>Impact </label>
              <SortArrows
                field="impact"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />
            </th> -->
            <th class="raytablehead valueColumn px-2">
              <label>Invalids </label>
              <SortArrows
                field="pinv"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />

            </th>
            <th class="raytablehead px-2 plotColumn">
              <label>Distribution </label>

            </th>
          </tr>
        </thead>
        <tbody>
          <FeatureRow
            v-for="(feature, name) in schemaSelection"
            :featureData="feature"
            :otherFeatureData="otherSelection[name]"
            :compareStats="reportComponents[name]"
            :key="name"
          />
        </tbody>
      </table>
      <Pagination
        :elements="schemaMatchedKeys"
        :ppp="ppp"
        :page="page"
        @pagechanged="changePage"
      />
    </div>

  </div>

</template>

<script>
// import { Plotly } from "vue-plotly";
import Pagination from "@/components/Pagination.vue";
import FeatureRow from "@/components/compare/FeatureRow.vue";
import SortArrows from "@/components/SortArrows.vue";
const octicons = require("@primer/octicons");
const PPP = 10; // Plots per page
export default {
  props: ["schemaDef", "otherDef", "compareStats", "componentType"],
  components: {
    Pagination,
    FeatureRow,
    SortArrows,
  },
  data: function () {
    return {
      featureFilter: "",
      page: 0,
      ppp: PPP,
      octicons,
      activeSortField: "name",
      activeSortDirection: "up",
    };
  },
  methods: {
    changePage(page) {
      this.page = page;
    },
    isActive(field, direction) {
      return (
        field === this.activeSortField && direction === this.activeSortDirection
      );
    },
    setActiveSort({ activeSortField, activeSortDirection }) {
      this.activeSortField = activeSortField;
      this.activeSortDirection = activeSortDirection;
    },
    getSortFunc() {
      let func = undefined;
      let featureData = this.profileComponents;
      if (this.activeSortField === "name") {
        func = (firstEl, secondEl) => {
          if (firstEl == secondEl) {
            return 0;
          } else if (firstEl < secondEl) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "type") {
        func = (firstEl, secondEl) => {
          if (
            featureData[firstEl].feature_class ===
            featureData[secondEl].feature_class
          ) {
            return 0;
          } else if (
            featureData[firstEl].feature_class <
            featureData[secondEl].feature_class
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "importance") {
        func = (firstEl, secondEl) => {
          if (
            featureData[firstEl].feature.importance ===
            featureData[secondEl].feature.importance
          ) {
            return 0;
          } else if (
            featureData[firstEl].feature.importance <
            featureData[secondEl].feature.importance
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "pvalue") {
        func = (firstEl, secondEl) => {
          if (
            this.compareStats[firstEl].pvalue ===
            this.compareStats[secondEl].pvalue
          ) {
            return 0;
          } else if (
            this.compareStats[firstEl].pvalue <
            this.compareStats[secondEl].pvalue
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "drift") {
        func = (firstEl, secondEl) => {
          if (
            this.compareStats[firstEl].drift ===
            this.compareStats[secondEl].drift
          ) {
            return 0;
          } else if (
            this.compareStats[firstEl].drift < this.compareStats[secondEl].drift
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "impact") {
        func = (firstEl, secondEl) => {
          if (
            this.compareStats[firstEl].impact ===
            this.compareStats[secondEl].impct
          ) {
            return 0;
          } else if (
            this.compareStats[firstEl].impact <
            this.compareStats[secondEl].impact
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "pinv") {
        func = (firstEl, secondEl) => {
          console.log("Using pinvdiff function");
          if (this.getPinvDiff(firstEl) === this.getPinvDiff(secondEl)) {
            return 0;
          } else if (this.getPinvDiff(firstEl) < this.getPinvDiff(secondEl)) {
            return -1;
          } else {
            return 1;
          }
        };
      } else {
        console.log("Unknown sort function", this.activeSortField);
      }
      return func;
    },
    getPinvDiff(featName) {
      return Math.abs(
        this.profileComponents.features[featName].feature.stats.pinv -
          this.otherProfileComponents.features[featName].feature.stats.pinv
      );
    },
  },
  computed: {
    profileComponents() {
      return this.schemaDef[this.componentType];
    },
    otherProfileComponents() {
      return this.otherDef[this.componentType];
    },
    reportComponents() {
      return this.compareStats[this.componentType];
    },
    activeSortObj() {
      return {
        activeSortField: this.activeSortField,
        activeSortDirection: this.activeSortDirection,
      };
    },
    schemaMatchedKeys() {
      let allKeys = Object.keys(this.profileComponents);
      let selectedKeys = allKeys;
      // filter
      if (this.featureFilter.length > 0) {
        selectedKeys = allKeys.filter((key) =>
          key.startsWith(this.featureFilter)
        );
      }
      return selectedKeys;
    },
    schemaSortedKeys() {
      let func = this.getSortFunc();
      let featureKeys = this.schemaMatchedKeys;

      featureKeys.sort(func);
      if (this.activeSortDirection === "down") {
        featureKeys.reverse();
      }
      return featureKeys;
    },
    schemaPageKeys() {
      let selectedKeys = this.schemaSortedKeys;
      selectedKeys = selectedKeys.slice(this.page * PPP, this.page * PPP + PPP);
      return selectedKeys;
    },
    schemaSelection() {
      const selectedKeys = this.schemaPageKeys;
      let schemaObj = {};
      for (const key of selectedKeys) {
        schemaObj[key] = this.profileComponents[key];
      }
      return schemaObj;
    },
    otherSelection() {
      const selectedKeys = this.schemaPageKeys;
      let otherObj = {};
      for (const key of selectedKeys) {
        otherObj[key] = this.otherProfileComponents[key];
      }
      return otherObj;
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
.tableWrapper {
  position: relative;
  overflow-x: auto;
  white-space: nowrap;
  display: block;
}
.hideScrollbar::-webkit-scrollbar {
  display: none;
}
.stickyCol {
  position: -webkit-sticky;
  position: sticky;
  /* background-color: white; */
}

.nameColumn {
  width: 200px;
  height: 30px;
}
.typeColumn {
  width: 100px;
}
.pvalueColumn {
  width: 150px;
}
.valueColumn {
  width: 50px;
}
.plotColumn {
  width: 100%;
}

.tableWrapper > table {
  table-layout: fixed;
  border-collapse: collapse;
  font-size: 14px;
  white-space: nowrap;

  /*border-spacing: 1px;*/
  /* border: 2px; */
}
tr.tableRayContentRow {
  line-height: 30px;
  min-height: 30px;
  max-height: 30px;
  overflow: auto;
  border-bottom: 1px solid #e1e4e8;
  background-color: white;
}

tr.tableRayContentRow:hover,
tr.tableRayContentRow:hover > td {
  background: #f6f8fa !important; /*primer bg-gray*/
}

.raytablehead {
  text-align: left;
  /* font-family: Helvetica; */
  font-style: normal;
  font-weight: 300;
  font-size: 12px;
  line-height: 40px;
  /* text-indent: 5px; */
  text-transform: uppercase;
  white-space: nowrap;
  border-bottom: 1px solid #e1e4e8;
  /* height: 5em; */
}
</style>
