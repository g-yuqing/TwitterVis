import Vue from 'vue'
import App from './App'
import {
  Select,
  Option,
  Dropdown,
  DropdownMenu,
  DropdownItem,
} from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

Vue.config.productionTip = false
Vue.use(Select)
Vue.use(Option)
Vue.use(Dropdown)
Vue.use(DropdownMenu)
Vue.use(DropdownItem)

const eventHub = new Vue()
Vue.mixin({
  data: () => ({eventHub})
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  components: { App },
  template: '<App/>'
})
