<template>
  <div id="app">
    <tsneview></tsneview>
    <el-tabs v-model="activeName" @tab-click="handleTabClick">
      <el-tab-pane label="Recurring" name="first">
        <recurringtab></recurringtab>
      </el-tab-pane>
      <el-tab-pane label="Leap" name="second">
        <leaptab></leaptab>
      </el-tab-pane>
      <el-tab-pane label="Worm" name="third">
        <wormtab></wormtab>
      </el-tab-pane>
    </el-tabs>
    <div id='detailed-view'></div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import TsneView from './components/TsneView'
import RecurringTab from './components/RecurringTab'
import LeapTab from './components/LeapTab'
import WormTab from './components/WormTab'


export default {
  name: 'App',
  components: {
    tsneview: TsneView,
    recurringtab: RecurringTab,
    leaptab: LeapTab,
    wormtab: WormTab,
  },
  data: () => ({
    activeName: 'second',
    topics: ['原発_稼働', '原発_東電', '原発_福島',
      '放射能_福島', '福島_避難', '原発_報道',
      '報道_福島', '安全_福島', '福島_被曝',
      '事故_原発', '原発_安全', '原発_電力',
      '復興_福島', '国民_東電', '東電_福島',
      '子供_福島', '政府_東電', '東電_社員',
      '原発_反対', '影響_福島'],
    timeStep: 31,
    moveStep: 7,
    timespanThres: 5,
  }),
  mounted() {
    this.loadData()
      .then(dataset => {
        this.graphData = dataset[0]  // {nodes:[], links: []}
        this.dateInfo = dataset[1]  // {date1: [{tid, text,count, tpc}, {}],}
        this.drawLayout()
        this.drawRecurringTab()
        this.drawWormTab()
        this.drawLeapTab()
      })
  },
  watch: {
  },
  methods: {
    async loadData() {
      const res = await fetch('../static/current/nodes.json')
      const graphData = await res.json()
      const res1 = await fetch('../static/current/date_info.json')
      const dateInfo = await res1.json()
      return [graphData, dateInfo]
    },
    // layout methods
    drawLayout() {
      this.eventHub.$emit('initTsnelayout', this.graphData)
    },
    drawRecurringTab() {
      function date2index(date) {
        const startDate = new Date('2011-03-11'),
          curDate = new Date(date),
          timeDiff = Math.abs(curDate.getTime() - startDate.getTime()),
          diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24))
        return diffDays/7
      }
      const parseDate = d3.timeFormat('%Y-%m-%d')
      // clusters: [{cluster, state, ndate, npos}]
      const clusters = this.graphData.clusters
      const nodes = this.graphData.nodes
      const lineData = [],
        tableData = []
      for(let i=20; i<clusters.length; i++) {
        const cluster = clusters[i],
          ndate = cluster.ndate
        if(cluster.state == 0 && ndate.length>0) {
          // [{date, rtptn, rate}, {}]
          let prevIdx = this.date2index(ndate[0])
          let prevDate = ndate[0]
          let tempRtptn = this.topics.map(() => 0)
          let firstDate = ndate[0]
          for(let j=0;j<ndate.length;j++) {
            // lineData
            const curIdx = this.date2index(ndate[j])
            const rtptn = nodes[curIdx].rtptn
              // rate = nodes[curIdx].rate
            if(curIdx-prevIdx>this.timespanThres) {
              const ratio = Math.max.apply(Math, tempRtptn) / 100
              lineData.push({
                group: lineData.length,
                rtptn: tempRtptn.map(num => num/ratio),
                start: firstDate,
                end: prevDate
              })
              firstDate = ndate[j]
              tempRtptn = this.topics.map(() => 0)
            }
            tempRtptn = tempRtptn.map((num, idx) => num+rtptn[idx])
            prevIdx = curIdx
            prevDate = ndate[j]
          }
          const startIdx = this.date2index(ndate[0]),
            endIdx = this.date2index(ndate[ndate.length-1])
          for(let j=startIdx; j<=endIdx; j++) {  // each day
            // tableData
            const infolist = this.dateInfo[nodes[j].date]
            for(let k=0;k<infolist.length;k++) {
              const info = infolist[k]
              if(info.tpc.length!=0) {
                //tableData
                tableData.push({
                  date: nodes[j].date,
                  text: info.text,
                  count: info.count,
                  topics: info.tpc.join('&')
                })
              }
            }
          }
          this.eventHub.$emit('renderRecurringTab', lineData, tableData)
          break
        }
      }
    },
    drawLeapTab() {
      const links = this.graphData.links
      for(let i=280; i<links.length; i++) {
        const link = links[i]
        if(link.state == 2) {
          d3.select(`#tsne-path${i}`)
            .style('stroke', '#FF2D55')
            .style('stroke-width', 3)
          const barData = [],
            tableData = [],
            srcNode = link.src,
            dstNode = link.dst
          const parseDate = d3.timeFormat('%Y-%m-%d')
          for(let j=0;j<this.moveStep;j++) {
            let curSrcDate = new Date(srcNode.date);
            curSrcDate.setDate(curSrcDate.getDate() + j)
            let curDstDate = new Date(dstNode.date);
            curDstDate.setDate(curDstDate.getDate() + j)
            const srcDate = parseDate(curSrcDate),
              dstDate = parseDate(curDstDate)
            const srcInfo = this.dateInfo[srcDate],
              dstInfo = this.dateInfo[dstDate]
            // push date info
            for(let i=0;i<srcInfo.length;i++) {
              const info = srcInfo[i]
              if(info.tpc.length!=0) {
                tableData.push({
                  date: srcNode.date,
                  text: info.text,
                  count: info.count,
                  topics: info.tpc.join('&')
                })
              }
            }
            for(let i=0;i<dstInfo.length;i++) {
              const info = dstInfo[i]
              if(info.tpc.length!=0) {
                tableData.push({
                  date: dstNode.date,
                  text: info.text,
                  count: info.count,
                  topics: info.tpc.join('&')
                })
              }
            }

          }
          for(let k=0; k<srcNode.tpc.length; k++) {
            barData.push(dstNode.tpc[k] - srcNode.tpc[k])
          }
          this.eventHub.$emit('renderLeapTab', barData, tableData)
          break
        }
      }
    },
    drawWormTab() {
      function date2index(date) {
        const startDate = new Date('2011-03-11'),
          curDate = new Date(date),
          timeDiff = Math.abs(curDate.getTime() - startDate.getTime()),
          diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24))
        return diffDays
      }
      const parseDate = d3.timeFormat('%Y-%m-%d')
      // clusters: [{cluster, state, ndate, npos}]
      const clusters = this.graphData.clusters
      const nodes = this.graphData.nodes
      const lineData = [],
        tableData = []
      for(let i=0; i<clusters.length; i++) {
        const cluster = clusters[i],
          ndate = cluster.ndate
        if(cluster.state == 1 && ndate.length>2) {
          // [{date, rtptn, rate}, {}]
          const startIdx = this.date2index(ndate[0]),
            endIdx = this.date2index(ndate[ndate.length-1])+this.timeStep
          for(let j=startIdx; j<=endIdx; j++) {  // each day
            let tempObj = {date: nodes[j].date}
            for(let k=0;k<this.topics.length;k++) {
              tempObj[this.topics[k]] = 0
            }
            const infolist = this.dateInfo[nodes[j].date]
            for(let k=0;k<infolist.length;k++) {
              const info = infolist[k]
              if(info.tpc.length!=0) {
                //lineData
                info.tpc.forEach(d => {
                  tempObj[d] += 1
                })
                //tableData
                tableData.push({
                  date: nodes[j].date,
                  text: info.text,
                  count: info.count,
                  topics: info.tpc.join('&')
                })
              }
            }
            lineData.push(tempObj)
          }
          this.eventHub.$emit('renderWormTab', lineData, tableData)
          break
        }
      }
    },
    date2index(date) {
      const startDate = new Date('2011-03-11'),
        curDate = new Date(date),
        timeDiff = Math.abs(curDate.getTime() - startDate.getTime()),
        diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24))
      return diffDays/this.moveStep
    },
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
