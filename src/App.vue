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
import * as dat from 'dat.gui'
// import Topiclayout from './scripts/topiclayout'
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
  }),
  mounted() {
    this.loadData()
      .then(dataset => {
        this.keywordData = dataset.keyword  // {period: {date: [[kw, score],]}, keywords:[[kw: score], []]}
        this.stateData = dataset.state  // {nodes:[], links: []}
        this.topicData = dataset.topic  // {date1: [{tid, text,count, tpc}, {}],}
        // state
        // state - init gui dat
        const guiData = {
          dataset: 'path0',
          ShowGroups: false,
          ChangeView: false,
        }
        this.gui.domElement.id = 'state-gui'
        this.gui.add(guiData, 'dataset', {
          '2011': 'path0',
          'GroupA': 'path1',
          'GroupB': 'path2',
          'GroupC': 'path3',
          'GroupD': 'path4',
          'GroupE': 'path5',
        })
        this.gui.add(guiData, 'ShowGroups').onChange(val => {
          if(val) {
            this.eventHub.$emit('showGroups')
          }
          else {
            this.eventHub.$emit('hideGroups')
          }
        })
        // this.gui.add(guiData, 'ChangeView').onChange(val => {
        //   if(val) {
        //     this.eventHub.$emit('updateStateView')
        //   }
        //   else {
        //     this.eventHub.$emit('resetOriginView')
        //   }
        // })
        document.getElementById('stateview').appendChild(this.gui.domElement)
        this.drawStateView()
        // topic
        // this.topiclayout.initScene(this.topicData)
        // keyword
        // this.drawKeywordView(this.keywordData.period)
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
      this.eventHub.$emit('initStateView', this.stateData, this.keywordData)
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
#stateview {
  width: 500px;
  height: 500px;
}
#topicview {
  position: relative;
  float: left;
  width: 500px;
  height: 500px;
}
#keywordview {
  width: 100%;
  height: 300px;
}
#state-gui {
  position: absolute;
  top: 2px;
  left: 2px;
}
</style>
