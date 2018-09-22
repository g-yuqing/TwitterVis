<template>
  <div id="app">
    <!-- <tsneview></tsneview> -->
    <textview></textview>
  </div>
</template>

<script>
import TsneView from './components/TsneView'
import TextView from './components/TextView'

export default {
  name: 'App',
  components: {
    tsneview: TsneView,
    textview: TextView,
  },
  data: () => ({
  }),
  mounted() {
    this.loadData()
      .then(dataset => {
        this.graphData = dataset
        this.drawLayout()
      })
  },
  watch: {
  },
  methods: {
    async loadData() {
      const res = await fetch('../static/current/nodes.json')
      const graphData = await res.json()
      return graphData
    },
    // layout methods
    drawLayout() {
      this.eventHub.$emit('initTsnelayout', this.graphData)
    },
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
.el-tag + .el-tag {
  margin-left: 7px;
}
.button-new-tag {
  margin-left: 10px;
  height: 32px;
  line-height: 30px;
  padding-top: 0;
  padding-bottom: 0;
}
.input-new-tag {
  width: 90px;
  margin-left: 10px;
  vertical-align: bottom;
}
</style>
