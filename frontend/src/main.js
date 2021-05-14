import Vue from 'vue'
import ViewSchemaWrapper from './ViewSchemaWrapper.vue'
import CompareSchemaWrapper from './CompareSchemaWrapper.vue'



Vue.config.productionTip = false

new Vue({
  render: h => h(ViewSchemaWrapper)
}).$mount('#app')
