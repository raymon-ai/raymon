<template>
  <div>
    <div class="d-flex flex-row flex-justify-begin mb-6">
      <div
        class="schemaDiv pl-2 mr-4"
        :style="{'border-left-color': colors.color_scale_gray_5}"
      >
        <h2 class="pt-0"> Profile: <span class="codeLike">
            {{refDef.name}}</span>
        </h2>
        <h5>Version: <span class="codeLike">
            {{refDef.version}}
          </span></h5>
      </div>
      <div
        v-if="alternativeA"
        class="schemaDiv pl-2 mr-4"
        :style="{'border-left-color': colors.color_scale_blue_5}"
      >
        <h2 class="pt-0"> Profile: <span class="codeLike">
            {{alternativeA.name}}</span>
        </h2>
        <h5>Version: <span class="codeLike">
            {{alternativeA.version}}
          </span></h5>
      </div>

      <div
        v-if="alternativeB"
        class="schemaDiv pl-2 mr-4"
        :style="{'border-left-color': colors.color_scale_red_5}"
      >
        <h2 class="pt-0"> Profile: <span class="codeLike">
            {{alternativeA.name}}</span>
        </h2>
        <h5>Version: <span class="codeLike">
            {{alternativeA.version}}
          </span></h5>
      </div>

      <!-- <a
        href="#"
        @click="goToMainView"
      >
        <Logo />
      </a> -->

    </div>
  </div>

</template>

<script>
import Logo from "@/components/Logo.vue";
import { colors } from "@/js/colors.js";
export default {
  props: ["refDef", "alternativeA", "alternativeB", "poi"],
  components: {},
  data: function () {
    return {
      colors,
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
