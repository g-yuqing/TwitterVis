<template>
  <div id="app">
    <stateview></stateview>
    <globalkeywordview></globalkeywordview>
    <streamview></streamview>
    <localkeywordview></localkeywordview>
    <div id="topicview"></div>
    <div id="tweetview"></div>
    <!-- <div id="topicview"></div>
    <div id="tweetview"></div> -->
    <!-- <div id="wordburst"></div> -->

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
    this.loadData()
      .then(dataset => {
        this.keywordData = dataset.keyword  // {period: {date: [[kw, score],]}, keywords:[[kw: score], []]}
        this.stateData = dataset.state  // {nodes:[], links: []}
        this.newsData = dataset.news  // {date: [{title, content}, {title, content}]}
        // state
        // state - init gui dat
        const guiData = {
          // TopicNumbers: 20,
          // TimeSpan: 5,
          // Submit: false,
          '2011': '',
          ShowGroups: false,
          ChangeDimension: false,
        }
        this.gui.domElement.id = 'state-gui'
        // const stateParam = this.gui.addFolder('parameters')
        // stateParam.add(guiData, 'TopicNumbers', 1, 80, 1)
        // stateParam.add(guiData, 'TimeSpan', 1, 14, 1)
        // stateParam.add(guiData, 'Submit')
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
          this.eventHub.$emit('initStateView', stateData, this.keywordData, this.newsData)
          this.eventHub.$emit('initStreamView', stateData, this.keywordData, this.newsData)
          this.eventHub.$emit('initGlobalKeywordView', stateData, this.keywordData)
        })
        this.gui.add(guiData, 'ShowGroups').onChange(val => {
          this.eventHub.$emit('switchStateShowGroups', val)
          this.eventHub.$emit('switchKeywordShowGroups', val)
        })
        this.gui.add(guiData, 'ChangeDimension').onChange(val => {
          this.eventHub.$emit('switchStateDimension', val)
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
      const res2 = await fetch('../static/news_database.json')
      const newsData = await res2.json()
      return {
        keyword: keywordData,
        state: stateData,
        news: newsData,
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
#state-gui {
  position: absolute;
  top: 2px;
  left: 2px;
}
#topicview {
  position: relative;
  float: left;
  width: 50%;
  height: 250px;
}
#tweetview {
  position: relative;
  float: left;
  width: 50%;
  height: 300px;
  overflow: auto;
}
/* #wordburst {
  position: relative;
  float: left;
  width: 900px;
  height: 900px;
} */
</style>
