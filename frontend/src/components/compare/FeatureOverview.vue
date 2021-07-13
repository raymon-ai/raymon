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
          placeholder="type a component name here..."
          id="componentfilter"
          v-model="componentFilter"
          @input="changePage(0)"
        />
      </dl>

    </div>

    <div class="tableWrapper hideScrollbar">
      <table>
        <thead>
          <tr>
            <th class="raytablehead nameColumn px-2">
              <label>Component </label>
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
                field="invalids"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />

            </th>
            <!-- <th class="raytablehead valueColumn px-2">
              <label>Mean </label>
              <SortArrows
                field="mean"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />
            </th> -->
            <th class="raytablehead px-2 plotColumn">
              <label>Distribution </label>

            </th>
          </tr>
        </thead>
        <tbody v-if="alternativeBSelection">
          <FeatureRow
            v-for="(component, name) in schemaSelection"
            :refComponentData="component"
            :alternativeAComponentData="alternativeASelection[name]"
            :alternativeBComponentData="alternativeBSelection[name]"
            :reportData="reportComponents[name]"
            :key="name"
          />

        </tbody>
        <tbody v-else>
          <FeatureRow
            v-for="(component, name) in schemaSelection"
            :refComponentData="component"
            :alternativeAComponentData="alternativeASelection[name]"
            :reportData="reportComponents[name]"
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
  props: [
    "refData",
    "alternativeA",
    "alternativeB",
    "reportData",
    "componentType",
  ],
  components: {
    Pagination,
    FeatureRow,
    SortArrows,
  },
  data: function () {
    return {
      componentFilter: "",
      page: 0,
      ppp: PPP,
      octicons,
      activeSortField: "name",
      activeSortDirection: "up",
      typeMapping: {
        Inputs: "InputComponent",
        Outputs: "OutputComponent",
        Actuals: "ActualComponent",
        Evaluations: "EvalComponent",
      },
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
      let componentData = this.profileComponents;
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
            componentData[firstEl].state.dtype ===
            componentData[secondEl].state.dtype
          ) {
            return 0;
          } else if (
            componentData[firstEl].state.dtype <
            componentData[secondEl].state.dtype
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "drift") {
        func = (firstEl, secondEl) => {
          if (
            this.reportComponents[firstEl].drift.drift ===
            this.reportComponents[secondEl].drift.drift
          ) {
            return 0;
          } else if (
            this.reportComponents[firstEl].drift.drift <
            this.reportComponents[secondEl].drift.drift
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "invalids") {
        func = (firstEl, secondEl) => {
          if (
            this.reportComponents[firstEl].invalids.invalids ===
            this.reportComponents[secondEl].invalids.invalids
          ) {
            return 0;
          } else if (
            this.reportComponents[firstEl].invalids.invalids <
            this.reportComponents[secondEl].invalids.invalids
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "mean") {
        func = (firstEl, secondEl) => {
          let firstElMean = this.reportComponents[firstEl].mean.mean;
          let secondElMean = this.reportComponents[secondEl].mean.mean;
          if (firstElMean == "-" && secondElMean == "-") {
            return 0;
          } else if (!(firstElMean == "-") && secondElMean == "-") {
            return 1;
          } else if (firstElMean == "-" && !(secondElMean == "-")) {
            return -1;
          } else if (firstElMean === secondElMean) {
            return 0;
          } else if (firstElMean < secondElMean) {
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
        this.profileComponents.components[featName].state.stats.state.invalids -
          this.alternativeAProfileComponents.components[featName].state.stats
            .state.invalids
      );
    },
  },
  computed: {
    profileComponents() {
      // return this.refData[this.componentType];
      let components = {};
      for (let [name, component] of Object.entries(this.refData.components)) {
        let parts = component.class.split(".");
        if (parts[parts.length - 1] == this.typeMapping[this.componentType]) {
          components[name] = component;
        }
      }
      return components;
    },
    alternativeAProfileComponents() {
      let components = {};
      for (let [name, component] of Object.entries(
        this.alternativeA.components
      )) {
        let parts = component.class.split(".");
        if (parts[parts.length - 1] == this.typeMapping[this.componentType]) {
          components[name] = component;
        }
      }
      return components;
    },
    alternativeBProfileComponents() {
      if (!this.alternativeB) {
        return undefined;
      }
      let components = {};
      for (let [name, component] of Object.entries(
        this.alternativeB.components
      )) {
        let parts = component.class.split(".");
        if (parts[parts.length - 1] == this.typeMapping[this.componentType]) {
          components[name] = component;
        }
      }
      return components;
    },
    sharedProfileComponents() {
      var keys = Object.keys(this.profileComponents);

      let common = keys.filter((x) => {
        return this.alternativeAProfileComponents[x] !== undefined;
      });

      if (this.alternativeBProfileComponents) {
        common = keys.filter((x) => {
          return this.alternativeAProfileComponents[x] !== undefined;
        });
      }
      return common;
    },
    reportComponents() {
      return this.reportData;
    },
    activeSortObj() {
      return {
        activeSortField: this.activeSortField,
        activeSortDirection: this.activeSortDirection,
      };
    },
    schemaMatchedKeys() {
      let allKeys = this.sharedProfileComponents;
      let selectedKeys = allKeys;
      // filter
      if (this.componentFilter.length > 0) {
        selectedKeys = allKeys.filter((key) =>
          key.startsWith(this.componentFilter)
        );
      }
      return selectedKeys;
    },
    schemaSortedKeys() {
      let func = this.getSortFunc();
      let componentKeys = this.schemaMatchedKeys;

      componentKeys.sort(func);
      if (this.activeSortDirection === "down") {
        componentKeys.reverse();
      }
      return componentKeys;
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
    alternativeASelection() {
      const selectedKeys = this.schemaPageKeys;
      let otherObj = {};
      for (const key of selectedKeys) {
        otherObj[key] = this.alternativeAProfileComponents[key];
      }
      return otherObj;
    },
    alternativeBSelection() {
      if (!this.alternativeBProfileComponents) {
        return undefined;
      }
      const selectedKeys = this.schemaPageKeys;
      let otherObj = {};
      for (const key of selectedKeys) {
        otherObj[key] = this.alternativeBProfileComponents[key];
      }
      return otherObj;
    },
  },
  watch: {
    componentType: function (n, o) {
      this.changePage(0);
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

.valueColumn {
  min-width: 150px;
  text-align: left;
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
