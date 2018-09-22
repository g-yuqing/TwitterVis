<template>
  <div id="textlayout">
    <div id="forcelayout"></div>
    <div id="texttable">
      <el-table
        :data="tableData"
        :height=tableHeight
        size="mini"
        empty-text="no data"
        border
        style="width: 100%">
        <el-table-column
          prop="date"
          label="date"
          width="100">
        </el-table-column>
        <el-table-column
          prop="author"
          label="author"
          width="100">
        </el-table-column>
        <el-table-column
          prop="text"
          label="text"
          width="400">
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'
export default {
  name: 'Textlayout',
  data: () => ({
    tableData: [],
    tableHeight: window.innerHeight
  }),
  watch: {
    tableData(val) {}
  },
  mounted() {
    // this.eventHub.$on('initTextlayoutScene', (data1, data2) => this.initScene(data1, data2))
    this.eventHub.$on('initTextlayoutScene', (data1, data2) => this.initScene(data1, data2))
  },
  methods: {
    initScene() {
      this.tableData = [{
        date: '2015-2-2',
        author: 'abc',
        text: 'test text'
      }]
    }
    initScene(layoutData, tweetData) {
      // layout
      this.tableData = []
      const width = window.innerWidth,
        height =  window.innerHeight
      document.getElementById('forcelayout').innerHTML = ''
      const svg = d3.select(document.getElementById('forcelayout')).append('svg')
        .attr('width', width/2)
        .attr('height', height)
      const nodeData = []
      for(const i in layoutData.nodes) {
        const obj = layoutData.nodes[i]
        if('degree' in obj) {
          nodeData.push(obj)
        }
        else {
          break
        }
      }
      const xScale = d3.scaleLinear()
        .domain(d3.extent(nodeData, d => d.x))
        .range([10, width/4-10])
      const yScale = d3.scaleLinear()
        .domain(d3.extent(nodeData, d => d.y))
        .range([height/3-10, 10])
      const node = svg.selectAll('.nodes')
        .data(nodeData).enter()
        .append('g')
        .attr('class', 'nodes')
        .on('click', d => {
          const obj = tweetData[d.name]
          console.log(d);
          const index = this.tableData.indexOf(obj)
          index == -1 ? this.tableData.unshift(obj) : this.tableData.splice(index, 1)
        })
      node.append('circle')
        .attr('cx', d => xScale(d.x))
        .attr('cy', d => yScale(d.y))
        .attr('r', d => d.size)
        .style('fill', d => d.color)
    }
  }
}
</script>

<style>
#forcelayout{
  position: relative;
  float: left;
}
#texttable {
  position: relative;
  float: right;
}
</style>
