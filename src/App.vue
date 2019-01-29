<template>
  <div id="app">
    <stateview></stateview>
    <!-- <globalkeywordview></globalkeywordview> -->
    <streamview></streamview>
    <localkeywordview></localkeywordview>
  </div>
</template>

<script>
import * as d3 from 'd3'
import * as dat from 'dat.gui'
import StateView from './components/StateView'
import StreamView from './components/StreamView'
import GlobalkeywordView from './components/GlobalkeywordView'
import LocalkeywordView from './components/LocalkeywordView'


export default {
  name: 'App',
  components: {
    stateview: StateView,
    streamview: StreamView,
    globalkeywordview: GlobalkeywordView,
    localkeywordview: LocalkeywordView
    // keywordview: KeywordView,
  },
  data: () => ({
    // control panel
    gui: new dat.GUI({autoPlace: false}),
  }),
  mounted() {
    const guiData = {
      'task1': '',
      'task2': '',
      'task3': '',
      ShowStateView: false,
      ShowStreamView: false,
      ShowLocalView: false
    }
    this.gui.domElement.id = 'state-gui'
    const dataSelector = this.gui.addFolder('testdata')
    dataSelector.add(guiData, 'task1', {  // ==========================task1
      '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
      '6': '6', '7': '7', '8': '8', '9': '9', '10': '10',
    }).onChange(val => {
      const path = `../static/user-experiment/task1/${+val<=5?'easy':'hard'}/${+val<=5?val:val-5}`
      this.loadData(path)
        .then(dataset => {
          this.keywordData = dataset.keyword  // {period: {date: [[kw, score],]}, keywords:[[kw: score], []]}
          this.stateData = dataset.state  // {nodes:[], links: []}
          this.newsData = {}
          this.eventHub.$emit('initStateView', this.stateData, this.keywordData, this.newsData)
          this.eventHub.$emit('initStreamView', this.stateData, this.keywordData, this.newsData)
          this.eventHub.$emit('initGlobalKeywordView', this.stateData, this.keywordData)
          this.eventHub.$emit('initLocalKeywordView', this.stateData, this.keywordData, this.newsData)
        })
    })
    dataSelector.add(guiData, 'task2', {  // ==========================task2
      '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
      '6': '6', '7': '7', '8': '8', '9': '9', '10': '10',
    }).onChange(val => {
      const path = `../static/user-experiment/task2/${+val<=5?'easy':'hard'}/${+val<=5?val:val-5}`
      this.loadData(path)
        .then(dataset => {
          this.keywordData = dataset.keyword  // {period: {date: [[kw, score],]}, keywords:[[kw: score], []]}
          this.stateData = dataset.state  // {nodes:[], links: []}
          this.newsData = {}
          this.eventHub.$emit('initStateView', this.stateData, this.keywordData, this.newsData)
          this.eventHub.$emit('initStreamView', this.stateData, this.keywordData, this.newsData)
          this.eventHub.$emit('initGlobalKeywordView', this.stateData, this.keywordData)
          this.eventHub.$emit('initLocalKeywordView', this.stateData, this.keywordData, this.newsData)
        })
    })
    dataSelector.add(guiData, 'task3', {  // ==========================task3
      '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
      '6': '6', '7': '7', '8': '8', '9': '9', '10': '10',
    }).onChange(val => {
      const path = `../static/user-experiment/task2/${+val<=5?'easy':'hard'}/${+val<=5?val:val-5}`
      this.loadData(path)
        .then(dataset => {
          this.keywordData = dataset.keyword  // {period: {date: [[kw, score],]}, keywords:[[kw: score], []]}
          this.stateData = dataset.state  // {nodes:[], links: []}
          this.newsData = {}
          this.eventHub.$emit('initStateView', this.stateData, this.keywordData, this.newsData)
          this.eventHub.$emit('initStreamView', this.stateData, this.keywordData, this.newsData)
          this.eventHub.$emit('initGlobalKeywordView', this.stateData, this.keywordData)
          this.eventHub.$emit('initLocalKeywordView', this.stateData, this.keywordData, this.newsData)
        })
    })
    this.gui.add(guiData, 'ShowStateView').onChange(val => {
      const dom = document.getElementById('stateview')
      console.log(val);
      val ? dom.style.visibility = 'visible' : dom.style.visibility = 'hidden'
    })
    this.gui.add(guiData, 'ShowStreamView').onChange(val => {
      const dom = document.getElementById('streamview')
      val ? dom.style.visibility = 'visible' : dom.style.visibility = 'hidden'
    })
    this.gui.add(guiData, 'ShowLocalView').onChange(val => {
      const dom = document.getElementById('local-keyword')
      val ? dom.style.visibility = 'visible' : dom.style.visibility = 'hidden'
    })
    document.getElementById('app').appendChild(this.gui.domElement)
  },
  watch: {
  },
  methods: {
    async loadData(path) {
      const res = await fetch(`${path}top-topics.json`)
      const keywordData = await res.json()
      const res1 = await fetch(`${path}state-graph.json`)
      const stateData = await res1.json()
      return {
        keyword: keywordData,
        state: stateData
      }
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
#state-gui {
  position: absolute;
  top: 3px;
  left: 2px;
}
#stateview {
  visibility: hidden;
}
#streamview {
  visibility: hidden;
}
#local-keyword {
  visibility: hidden;
}
#global-keyword {
  visibility: hidden;
}
#newsview {
  position: relative;
  float: left;
  width: 45%;
  height: 500px;
  overflow: auto;
  background-color: hsla(0,0%,100%,0.7);
  padding: 10px;
  border-radius: 5px;
  font-size: 7px;
}
#topicview {
  position: relative;
  float: left;
  width: 45%;
  height: 200px;
}
#tweetview {
  position: relative;
  float: left;
  width: 45%;
  height: 300px;
  overflow: auto;
}
.newsview .title {
  font-weight: 900;
  font-size: 12px;
  margin-bottom: 2px;
}
.newsview .content {
  font-weight: 900;
  font-size: 9px;
  color: #E8175D;
}
.tweetview .count {
  font-weight: 900;
  font-size: 12px;
  margin-bottom: 2px;
  color: #E8175D;
}
.tweetview .tweet {
  font-weight: 900;
  font-size: 9px;
}
</style>
