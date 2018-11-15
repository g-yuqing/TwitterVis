<template>
  <div id="app">
    <!-- state view -->
    <stateview></stateview>
    <!-- topic view -->
    <div id="topicview"></div>
    <!-- keyword view -->
    <keywordview></keywordview>
  </div>
</template>

<script>
import * as d3 from 'd3'
// import * as moment from 'moment'
import * as dat from 'dat.gui'
import Topiclayout from './scripts/topiclayout'
import StateView from './components/StateView'
import KeywordView from './components/KeywordView'


export default {
  name: 'App',
  components: {
    stateview: StateView,
    keywordview: KeywordView,
  },
  data: () => ({
    // control panel
    gui: new dat.GUI({autoPlace: false}),
    topiclayout: new Topiclayout(),
  }),
  mounted() {
    this.loadData()
      .then(dataset => {
        this.keywordData = dataset.keyword  // {period: {date: [[kw, score],]}, keywords:[[kw: score], []]}
        this.stateData = dataset.state  // {nodes:[], links: []}
        this.topicData = dataset.topic  // {date1: [{tid, text,count, tpc}, {}],}
        // state
        const guiData = {
          text: 'test data',
          PCAView: false
        }
        this.gui.add(guiData, 'text')
        this.gui.add(guiData, 'PCAView').onChange(val => {
          if(val) {
            this.eventHub.$emit('updateStateView')
          }
          else {
            this.eventHub.$emit('resetOriginView')
          }
        })
        const controlPanel = document.getElementById('stateview').appendChild(this.gui.domElement)
        this.drawStateView()
        // topic
        this.topiclayout.initScene(this.topicData)
        // keyword
        this.drawKeywordView(this.keywordData.period)
      })
  },
  watch: {
  },
  methods: {
    async loadData() {
      const res = await fetch('../static/top_keywords.json')
      const keywordData = await res.json()
      const res1 = await fetch('../static/state_graph.json')
      const stateData = await res1.json()
      const res2 = await fetch('../static/topic_graph.json')
      const topicData = await res2.json()
      return {
        keyword: keywordData,
        state: stateData,
        topic: topicData
      }
    },
    // layout methods
    drawStateView() {
      this.eventHub.$emit('initStateView', this.stateData)
    },
    drawKeywordView(dataset) {
      const data = [
        {date: '2011-03-21', kwscore: dataset['2011-03-21']},
        {date: '2011-03-22', kwscore: dataset['2011-03-22']},
        {date: '2011-03-23', kwscore: dataset['2011-03-23']},
        {date: '2011-03-24', kwscore: dataset['2011-03-24']},
        {date: '2011-03-25', kwscore: dataset['2011-03-25']}
      ]
      this.eventHub.$emit('initKeywordView', data)
    }
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
#topicview {
  position: relative;
  float: left;
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
