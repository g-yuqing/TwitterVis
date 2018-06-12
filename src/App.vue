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
    <splatting></splatting>
    <canvas id="word_canvas"></canvas>
  </div>
</template>

<script>
import Splatting from './components/SplattingView'
export default {
  name: 'App',
  components: {
    splatting: Splatting,
  },
  data: () => ({
    dataset: [],
    word_data: null,
    contour_data: null,
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
      .then(dataset => {
        this.word_data = dataset.word_data
        this.contour_data = dataset.contour_data
        this.drawSplatting(this.year)
      })
  },
  watch: {
    year(val) {
      this.drawSplatting(val)
    }
  },
  methods: {
    async loadData() {
      let res = await fetch('../static/clustered/word_clouds.json')
      const word_data = await res.json()
      res = await fetch('../static/clustered/cluster_contours.json')
      const contour_data = await res.json()
      return {word_data: word_data, contour_data: contour_data}
    },
    drawSplatting(year) {
      const index = this.years[year].label
      this.eventHub.$emit('initSplattingScene', this.contour_data[index], this.word_data[index])
    }
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
