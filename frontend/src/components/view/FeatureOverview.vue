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
            <!-- <th class="raytablehead typeColumn px-2">
              <label>Imp. </label>
              <SortArrows
                field="importance"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />
            </th> -->

            <th class="raytablehead valueColumn px-2">
              <label>Min </label>
              <SortArrows
                field="min"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />

            </th>
            <th class="raytablehead valueColumn px-2">
              <label>Max </label>
              <SortArrows
                field="max"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />

            </th>
            <th class="raytablehead valueColumn px-2">
              <label>Invalids </label>
              <SortArrows
                field="invalids"
                :active="activeSortObj"
                @activeSortChanged="setActiveSort"
              />

            </th>
            <th class="raytablehead px-2 plotColumn">
              <label>Plot </label>

            </th>
          </tr>
        </thead>
        <tbody>
          <FeatureRow
            v-for="(component, name) in schemaSelection"
            :componentData="component"
            :poi="poi[name]"
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
import FeatureRow from "@/components/view/FeatureRow.vue";
import SortArrows from "@/components/SortArrows.vue";
const octicons = require("@primer/octicons");
const PPP = 10; // Plots per page
export default {
  props: ["refDef", "poi", "componentType"],
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
      } else if (this.activeSortField === "min") {
        func = (firstEl, secondEl) => {
          if (
            componentData[firstEl].state.stats.state.min ===
            componentData[secondEl].state.stats.state.min
          ) {
            return 0;
          } else if (
            typeof componentData[firstEl].state.stats.state.min === "undefined"
          ) {
            return -1;
          } else if (
            componentData[firstEl].state.stats.state.min <
            componentData[secondEl].state.stats.state.min
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "max") {
        func = (firstEl, secondEl) => {
          if (
            componentData[firstEl].state.stats.state.max ==
            componentData[secondEl].state.stats.state.max
          ) {
            return 0;
          } else if (
            typeof componentData[firstEl].state.stats.state.max === "undefined"
          ) {
            return -1;
          } else if (
            componentData[firstEl].state.stats.state.max <
            componentData[secondEl].state.stats.state.max
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "invalids") {
        func = (firstEl, secondEl) => {
          console.log("Using invalids function");
          if (
            componentData[firstEl].state.stats.state.invalids ==
            componentData[secondEl].state.stats.state.invalids
          ) {
            return 0;
          } else if (
            componentData[firstEl].state.stats.state.invalids <
            componentData[secondEl].state.stats.state.invalids
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else {
        console.log("Unknown sort function");
      }
      return func;
    },
  },
  computed: {
    profileComponents() {
      let components = {};
      for (let [name, component] of Object.entries(this.refDef.components)) {
        let parts = component.class.split(".");
        if (parts[parts.length - 1] == this.typeMapping[this.componentType]) {
          components[name] = component;
        }
      }
      return components;
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
      let newObj = {};
      for (const key of selectedKeys) {
        newObj[key] = this.profileComponents[key];
      }
      return newObj;
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
  font-style: normal;
  font-weight: 300;
  font-size: 12px;
  line-height: 40px;
  text-transform: uppercase;
  white-space: nowrap;
  border-bottom: 1px solid #e1e4e8;
}
</style>
