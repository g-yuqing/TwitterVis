<template>
  <div id="app">
    <!-- keyword list -->
    <!-- <div id="keywordlist">
      <el-row>
        <el-checkbox-group v-model="checkboxGroup" size="mini">
          <el-checkbox-button v-for="keyword in keywords"
            :label="keyword"
            :key="keyword">{{keyword}}
          </el-checkbox-button>
        </el-checkbox-group>
      </el-row>
    </div> -->
    <!-- state view -->
    <stateview></stateview>
    <!-- topic view -->
    <div id="topicview"></div>
    <!-- tab view -->
    <!-- <el-tabs v-model="activeName" @tab-click="handleTabClick">
      <el-tab-pane label="Recurring" name="first">
      </el-tab-pane>
      <el-tab-pane label="Leap" name="second">
      </el-tab-pane>
      <el-tab-pane label="Worm" name="third">
      </el-tab-pane>
    </el-tabs> -->
    <div id='detailed-view'></div>
  </div>
</template>

<script>
import * as d3 from 'd3'
// import * as moment from 'moment'
import * as dat from 'dat.gui'
import Topiclayout from './scripts/topiclayout'
import StateView from './components/StateView'


export default {
  name: 'App',
  components: {
    stateview: StateView,
  },
  data: () => ({
    // control panel
    gui: new dat.GUI({autoPlace: false}),
    // // keyword parameters
    // checkboxGroup: [],
    // keywords: [],
    // tab parameters
    activeName: 'second',
    topiclayout: new Topiclayout(),
  }),
  mounted() {
    this.loadData()
      .then(dataset => {
        this.keywordData = dataset.keyword  // {period: {date: [[kw, score],]}, keywords:[[kw: score], []]}
        this.stateData = dataset.state  // {nodes:[], links: []}
        this.topicData = dataset.topic  // {date1: [{tid, text,count, tpc}, {}],}
        // // keywords
        // this.keywords = this.keywordData.period['2011-03-11'].map(d => d[0])
        // this.allkeywords = this.keywordData.keywords.map(d => d[0])
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
      })
  },
  watch: {
    // checkboxGroup(val) {
    //   // console.log(this.allkeywords.length)
    //   // const valIdxs = new Array(this.allkeywords.length).fill(0)
    //   // for(const i in val) {
    //   //   const idx = this.allkeywords.indexOf(val[i])
    //   //   valIdxs[idx] = 1
    //   // }
    //   // // this.eventHub.$emit('updateStateView', valIdxs)
    //   // this.eventHub.$emit('showCluster')
    //   this.eventHub.$emit('updateClusterView')
    // }
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
    // tab view
    handleTabClick(tab, event) {}
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
