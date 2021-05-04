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
                field="pinv"
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
  props: ["schemaDef", "poi", "componentType"],
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
            componentData[firstEl].component_class ===
            componentData[secondEl].component_class
          ) {
            return 0;
          } else if (
            componentData[firstEl].component_class <
            componentData[secondEl].component_class
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "importance") {
        func = (firstEl, secondEl) => {
          if (
            componentData[firstEl].component.importance ===
            componentData[secondEl].component.importance
          ) {
            return 0;
          } else if (
            componentData[firstEl].component.importance <
            componentData[secondEl].component.importance
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "min") {
        func = (firstEl, secondEl) => {
          if (
            componentData[firstEl].component.stats.min ===
            componentData[secondEl].component.stats.min
          ) {
            return 0;
          } else if (
            typeof componentData[firstEl].component.stats.min === "undefined"
          ) {
            return -1;
          } else if (
            componentData[firstEl].component.stats.min <
            componentData[secondEl].component.stats.min
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "max") {
        func = (firstEl, secondEl) => {
          if (
            componentData[firstEl].component.stats.max ==
            componentData[secondEl].component.stats.max
          ) {
            return 0;
          } else if (
            typeof componentData[firstEl].component.stats.max === "undefined"
          ) {
            return -1;
          } else if (
            componentData[firstEl].component.stats.max <
            componentData[secondEl].component.stats.max
          ) {
            return -1;
          } else {
            return 1;
          }
        };
      } else if (this.activeSortField === "pinv") {
        func = (firstEl, secondEl) => {
          console.log("Using pinv function");
          if (
            componentData[firstEl].component.stats.pinv ==
            componentData[secondEl].component.stats.pinv
          ) {
            return 0;
          } else if (
            componentData[firstEl].component.stats.pinv <
            componentData[secondEl].component.stats.pinv
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
      return this.schemaDef[this.componentType];
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
