<template>
  <div id="layout">
    <div id="mdslayout"></div>
    <div id="texttable">
      <el-table
        :data="tableData"
        :height=tableHeight
        :row-class-name="tableRowClassName"
        size="mini"
        empty-text="no data"
        border
        style="width: 100%">
        <el-table-column
          prop="count"
          label="count"
          width="100">
        </el-table-column>
        <el-table-column
          prop="text"
          label="tweet-text"
          width="400">
        </el-table-column>
      </el-table>
    </div>
    <div id="timeline"></div>
    <div id="main-container"></div>
    <div id="egolayout"></div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import drawTimeline from '../scripts/timeline'
import drawEgolayout from '../scripts/egolayout'


export default {
  name: 'Layout',
  data: () => ({
    // table parameter
    tableData: [],
    tableHeight: window.innerHeight,
    // mds parameter
    colors: ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
      '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',
      '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000',
      '#ffd8b1', '#000080', '#808080', '#FFFFFF', '#000000']
  }),
  mounted() {
    this.eventHub.$on('initLayoutScene', (dataset, tags) => this.initScene(dataset, tags))
    this.eventHub.$on('updateLayoutScene', tags => this.updateScene(tags))
  },
  watch: {
    tableData(val) {},
  },
  methods: {
    // table methods
    tableRowClassName({row, rowIndex}) {
      if (rowIndex === 0) {
        return 'first-row'
      }
      else {
        return ''
      }
    },
    // mdslayout methods
    initScene(dataset, tags) {
      this.mdsData = dataset.mds
      const egoData = dataset.ego
      this.tagData = dataset.tag
      const tidtime = dataset.tidtime
      const tidtext = dataset.tidtext

      // extend tag
      const keywords = []
      tags.forEach(d => {
        this.tagData[d].forEach(dd => {
          keywords.push(dd)
        })
      })
      const tidList = []  // aviod repeatition

      const margin = {top: 30, right: 50, bottom: 10, left:20},
        width = window.innerWidth,
        height = window.innerHeight,
        cellWidth = 150,
        cellHeight = 150,
        cellSpace = 10
      const svg = d3.select(document.getElementById('mdslayout')).append('svg')
        .attr('id', 'mds-svg')
        .attr('width', cellWidth*7+cellSpace*6 + margin.left + margin.right)
        .attr('height', cellHeight + margin.top + margin.bottom)
      // year title
      const titleData = [
        {text: '2011', x: margin.left+cellWidth*0.5, y: margin.top},
        {text: '2012', x: margin.left+cellWidth*1.5 + cellSpace*1, y: margin.top},
        {text: '2013', x: margin.left+cellWidth*2.5 + cellSpace*2, y: margin.top},
        {text: '2014', x: margin.left+cellWidth*3.5 + cellSpace*3, y: margin.top},
        {text: '2015', x: margin.left+cellWidth*4.5 + cellSpace*4, y: margin.top},
        {text: '2016', x: margin.left+cellWidth*5.5 + cellSpace*5, y: margin.top},
        {text: '2017', x: margin.left+cellWidth*6.5 + cellSpace*6, y: margin.top}
      ]
      svg.selectAll('.title')
        .data(titleData)
        .enter().append('g')
        .append('text')
        .attr('x', d => d.x)
        .attr('y', d => d.y)
        .style('text-anchor', 'middle')
        .style('font-size', '17px')
        .style('fill', 'steelblue')
        .text(d => d.text)
      // adjust data positions
      const xScale = d3.scaleLinear()
        .range([0, cellWidth])
        .domain(d3.extent(this.mdsData, d => d.x))
      const yScale = d3.scaleLinear()
        .range([cellHeight, 0])
        .domain(d3.extent(this.mdsData, d => d.y))
      const year_nodes = {}
      const year_positions = {}
      this.mdsData.forEach((d, i) => {
        d.id = i
        d.x = xScale(d.x)+(+d.year-2011)*(cellWidth+cellSpace)
        d.y = yScale(d.y)
        // init datatable
        for(const t in keywords) {
          const tag = keywords[t]
          if(d.noun.includes(tag) && !tidList.includes(d.tid)) {
            tidList.push(d.tid)
            this.tableData.push({count:d.cotids[0][1], text: d.text})
          }
        }
      })
      // sort datatable
      this.tableData.sort((x, y) => d3.descending(x.count, y.count))
      // draw mds nodes
      const g = svg.append('g')
        .attr('id', 'mds-g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
      g.selectAll('.mdsdot').data(this.mdsData)
        .enter().append('circle')
        .attr('r', 2.5)
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .style('fill', d => {
          for(const t in keywords) {
            const tag = keywords[t]
            if(d.noun.includes(tag)) {
              return '#e6194b'
            }
          }
          return '#80808033'
        })
        .on('click', d => {
          // set selected point
          d3.select('#selected-g').selectAll('circle')
            .attr('cx', d.x)
            .attr('cy', d.y)
            .style('fill', '#3cb44b')
          const cotweets = d.cotids.map(dd => dd[0])
          g.selectAll('circle').style('stroke', dd => cotweets.includes(dd.tid)?'#000':null)
          // draw timeline
          drawTimeline(tidtime[d.tid])
          // draw ego network
          drawEgolayout(egoData[d.tid])
        })
      //init scene
      // init selected node
      const initData = this.mdsData[0]
      svg.append('g')
        .attr('id', 'selected-g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
        .selectAll('.dot').data([initData])
        .enter().append('circle')
        .attr('r', 4)
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .style('fill', '#3cb44b')
      // init contour of related nodes
      const cotweets = initData.cotids.map(dd => dd[0])
      g.selectAll('circle').style('stroke', dd => cotweets.includes(dd.tid)?'#000':null)
      // init timeline
      drawTimeline(tidtime[initData.tid])
      // init ego network
      drawEgolayout(egoData[initData.tid])
    },
    updateScene(tags) {
      const keywords = []  // extend tag
      const tidList = []  // aviod repeatition
      tags.forEach(d => {
        this.tagData[d].forEach(dd => {
          keywords.push(dd)
        })
      })
      console.log(keywords);
      d3.select('#mds-g').selectAll('circle')
        .style('fill', d => {
          for(const t in keywords) {
            const tag = keywords[t]
            if(d.noun.includes(tag)) {
              return '#e6194b'
            }
          }
          return '#80808033'
        })
      // set datatable
      this.tableData = []
      this.mdsData.forEach((d, i) => {
        for(const t in keywords) {
          const tag = keywords[t]
          if(d.noun.includes(tag) && !tidList.includes(d.tid)) {
            tidList.push(d.tid)
            this.tableData.push({count:d.cotids[0][1], text: d.text})
          }
        }
      })
      // sort datatable
      this.tableData.sort((x, y) => d3.descending(x.count, y.count))
    },
  }
}
</script>

<style>
  #mdslayout {
    position: relative;
    float: left;
  }
  #texttable {
    position: relative;
    float: right;
  }
  #timeline {
    position: relative;
    float: left;
  }
  #main-container {
    position: relative;
    float: left;
  }
  /* table parameter */
  .el-table .first-row {
    background: #f0f9eb;
  }
  .dot {
  }
  .ego-edges {
    stroke: #999;
    stroke-opacity: 0.6;
  }
  .ego-nodes {
    stroke: #fff;
    stroke-width: 1.5px;
  }
 /* .axis path,
 .axis line{
   fill: none;
   stroke-width: 1px;
   stroke: #777;
 } */
</style>
