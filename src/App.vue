<template>
  <div id="app">
    <!-- state view -->
    <stateview></stateview>
    <!-- keyword view -->
    <keywordview></keywordview>
    <!-- topic view -->
    <div id="topicview"></div>
    <div id="tweetview"></div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import * as dat from 'dat.gui'
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
          '2011': '',
          ShowGroups: false,
          ChangeView: false,
        }
        this.gui.domElement.id = 'state-gui'
        const dateSelector = this.gui.addFolder('dataset')
        dateSelector.add(guiData, '2011', {
          '2011': '0-291',
          'Mar. Apr.': '0-50',
          'May. Jun.': '51-111',
          'Jul. Aug.': '112-173',
          'Sep. Oct.': '174-234',
          'Nov. Dec.': '235-291',  // to 12/27
        }).onChange(val => {
          const ext = val.split('-'),
            start = +ext[0],
            end = +ext[1]
          const stateData = {
            nodes: this.stateData.nodes.slice(start, end+1),
            links: this.stateData.links.slice(start, end)}
          this.eventHub.$emit('initStateView', stateData, this.keywordData)
        })
        this.gui.add(guiData, 'ShowGroups').onChange(val => {
          this.eventHub.$emit('switchStateShowGroups', val)
          this.eventHub.$emit('switchKeywordShowGroups', val)
        })
        // state - graph view
        document.getElementById('app').appendChild(this.gui.domElement)
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
  position: relative;
  float: left;
  width: 30%;
  height: 500px;
}
#keywordview {
  width: 65%;
  height: 500px;
}
#topicview {
  position: relative;
  float: left;
  width: 65%;
  height: 250px;
}
#state-gui {
  position: absolute;
  top: 2px;
  left: 2px;
}
#tweetview {
  position: relative;
  float: left;
  width: 65%;
  height: 220px;
  overflow: auto;
}
</style>
