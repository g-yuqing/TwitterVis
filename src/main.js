import Vue from 'vue'
import App from './App'
import {
  Select,
  Option,
  Dropdown,
  DropdownMenu,
  DropdownItem,
  Pagination,
  Input,
  Form,
  FormItem,
  Table,
  TableColumn,
  Button,
  Tag,
  Tabs,
  TabPane,
} from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

Vue.config.productionTip = false
Vue.use(Select)
Vue.use(Option)
Vue.use(Dropdown)
Vue.use(DropdownMenu)
Vue.use(DropdownItem)
Vue.use(Pagination)
Vue.use(Input)
Vue.use(Form)
Vue.use(FormItem)
Vue.use(Table)
Vue.use(TableColumn)
Vue.use(Button)
Vue.use(Tag)
Vue.use(Tabs)
Vue.use(TabPane)
Vue.config.lang = 'en'


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
