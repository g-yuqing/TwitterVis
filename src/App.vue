<template>
  <div id="app">
    <div id="selector">
      <el-select v-model="year" placeholder="2011">
        <el-option
          v-for="y in years"
          :key="y.value"
          :label="y.label"
          :value="y.value">
        </el-option>
      </el-select>
    </div>
    <forcelayout></forcelayout>
  </div>
</template>

<script>
import Forcelayout from './components/ForcelayoutView'
export default {
  name: 'App',
  components: {
    forcelayout: Forcelayout,
  },
  data: () => ({
    dataset: [],
    year: 0,
    years: [
      {value: 0, label: '2011'},
      {value: 1, label: '2012'},
      {value: 2, label: '2013'},
      {value: 3, label: '2014'},
      {value: 4, label: '2015'},
      {value: 5, label: '2016'},
      {value: 6, label: '2017'},
    ]
  }),
  mounted() {
    this.loadData()
    this.drawForcelayout(this.year)
  },
  watch: {
    year(val) {
      this.drawForcelayout(val)
    }
  },
  methods: {
    loadData() {
      const filename = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
      for(let i=0;i<filename.length;i++) {
        const data = fetch('../static/march/'+filename[i]+'.json').then(res => res.json())
        this.dataset.push(data)
      }
    },
    drawForcelayout(year) {
      Promise.all(this.dataset).then(dataset => {
        this.eventHub.$emit('initForcelayoutScene', dataset[year])
      })
    },
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* text-align: center; */
  color: #2c3e50;
  /* margin-top: 60px; */
}
</style>
