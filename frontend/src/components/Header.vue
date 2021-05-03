<template>
  <div>
    <div class="d-flex flex-row-reverse flex-justify-between">
      <a
        href="#"
        @click="goToMainView"
      >
        <Logo />
      </a>
      <!-- <Logo class="mr-2" /> -->
      <div
        v-if="otherDef"
        class="schemaDiv pl-2"
        :style="{'border-left-color': red}"
      >
        <h2 class="pt-0"> Schema: <span class="codeLike">
            {{otherDef.name}}</span>
        </h2>
        <h5>Version: <span class="codeLike">
            {{otherDef.version}}
          </span></h5>
      </div>
      <div
        class="schemaDiv pl-2"
        :style="{'border-left-color': blue}"
      >
        <h2 class="pt-0"> Schema: <span class="codeLike">
            {{schemaDef.name}}</span>
        </h2>
        <h5>Version: <span class="codeLike">
            {{schemaDef.version}}
          </span></h5>
      </div>

    </div>
  </div>

</template>

<script>
import Logo from "@/components/Logo.vue";
import { red, green, blue } from "@/colors.js";
export default {
  props: ["schemaDef", "otherDef", "poi"],
  components: { Logo },
  data: function () {
    return {
      red,
      green,
      blue,
    };
  },
  methods: {
    goToMainView() {
      this.$emit("setPage", undefined);
    },
  },
  computed: {},
};
</script>
<style lang ="scss">
.schemaDiv {
  border-left: 10px;
  /* border-left-color: blue; */
  border-left-style: solid;
}
</style>
