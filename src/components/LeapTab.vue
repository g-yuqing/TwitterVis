<template>
  <div id="leaptab">
    <el-table
      :data="tableData"
      size="small"
      style="width: 100%"
      height="250">
      <el-table-column
        prop="topics"
        label="keywords"
        width="120">
      </el-table-column>
      <el-table-column
        prop="date"
        label="date"
        width="100">
      </el-table-column>
      <el-table-column
        prop="count"
        label="count"
        width="60">
      </el-table-column>
      <el-table-column
        prop="text"
        label="text"
        width="800">
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import * as d3 from 'd3'
export default {
  name: 'Leaptab',
  data: () => ({
        tableData: [],
  }),
  mounted() {
    // document.getElementById('leaptab').innerHTML = ''
    this.eventHub.$on('renderLeapTab', (data1, data2) => this.drawBarChart(data1, data2))
  },
  watch: {
    tableData(val) {
    },
  },
  methods: {
    drawBarChart(data1, data2) {
      // data1 format is expected to be
      // [{}, {}]
      this.tableData = data2
      const width = 400,
        height = 300,
        margin = {top: 30, right: 70, bottom: 50, left:70},
        colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
          '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',
          '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000',
          '#ffd8b1', '#000080', '#808080', '#FFFFFF', '#000000'],
        topics = ['原発_稼働', '原発_東電', '原発_福島',
          '放射能_福島', '福島_避難', '原発_報道',
          '報道_福島', '安全_福島', '福島_被曝',
          '事故_原発', '原発_安全', '原発_電力',
          '復興_福島', '国民_東電', '東電_福島',
          '子供_福島', '政府_東電', '東電_社員',
          '原発_反対', '影響_福島']
        const xScale = d3.scaleLinear()
          .domain(d3.extent(data1))
          .range([0, width])
        const yScale = d3.scaleBand()
          .domain(topics)
          .rangeRound([0, height])
          .padding(0.1)
        const xAxis = d3.axisBottom(xScale)
        const yAxis = d3.axisLeft(yScale)
        const barData = []
        for(let i=0; i<data1.length; i++) {
          barData.push({
            topic: topics[i],
            value: +data1[i]})
        }
        const svg = d3.select(document.getElementById('leaptab')).append('svg')
          .attr('id', 'leaptab-svg')
          .attr('width', width + margin.left + margin.right)
          .attr('height', height + margin.top + margin.bottom)
        const g = svg.append('g')
          .attr('id', 'leaptab-g')
          .attr('transform', `translate(${margin.left}, ${margin.top})`)
        g.append('g')
          .attr('class', 'axis')
          .attr('transform', `translate(0, ${height})`)
          .call(xAxis)
        const yG = g.append('g')
          .attr('class', 'axis')
          .attr('transform', `translate(${xScale(0)}, 0)`)
          .call(yAxis)
          .selectAll(".tick")
			    .filter((d, i) => barData[i].value<0)
        yG.selectAll('line')
          .attr('x2', 6)
        yG.selectAll('text')
          .attr('x', 9)
          .style('text-anchor', 'start')
        g.selectAll(".leaptab-bar")
          .data(barData)
          .enter().append('rect')
          .attr('class', 'leaptab-bar')
          .attr('x', d => xScale(Math.min(0, d.value)))
          .attr('y', d => yScale(d.topic))
          .attr('height', yScale.bandwidth())
          .attr('width', d => Math.abs(xScale(d.value)-xScale(0)))
          .style('fill', d => d.value>0?'steelblue':'darkorange')
    }
  }
}
</script>

<style>
#leaptab {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
  filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) );
}
</style>
