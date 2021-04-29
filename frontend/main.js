import Vue from 'vue'
import ViewSchemaWrapper from './ViewSchemaWrapper.vue'
import CompareSchemaWrapper from './CompareSchemaWrapper.vue'


import store from './store/store.js'

Vue.config.productionTip = false

new Vue({
  store,
  render: h => h(CompareSchemaWrapper)
}).$mount('#app')
