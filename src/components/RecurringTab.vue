<template>
  <div id="recurringtab">
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
  name: 'Recurringtab',
  data: () => ({
    tableData: [],
  }),
  mounted() {
    this.eventHub.$on('renderRecurringTab', (data1,data2) => this.drawBarChart(data1, data2))
  },
  watch: {
    tableData(val) {
    },
  },
  methods: {
    drawBarChart(data1, data2) {
      // data1 expected to be
      // {group1: [tpc1, tpc2, tpc3], group2: [tpc1, tpc2, tpc3], group3: [tpc1, tpc2, tpc3]}
      // [{group:0, rtptn: [], date}, {}, {}]
      this.tableData = data2
      const width = 700,
        height = 300,
        margin = {top: 30, right: 150, bottom: 150, left:50},
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
      // top 4 topics
      let indices = new Array(topics.length)
      for(let i=0;i<topics.length;i++) {indices[i] = i}
      const test = data1[0].rtptn
      indices.sort((a, b) => test[a] > test[b] ? -1 : test[a] < test[b] ? 1 : 0)
      indices = indices.slice(0, 4)
      const barData = data1.map(d => {
        return {
          group: d.group,
          start: d.start,
          end: d.end,
          rtptn: indices.map(dd => d.rtptn[dd])
        }
      })
      let yMax = 0
      for(let i=0;i<barData.length;i++) {
        const temp = d3.max(barData[i].rtptn)
        if(temp>yMax){
          yMax = temp
        }
      }
      const perGroup = d3.range(barData[0].rtptn.length)
      const xScale = d3.scaleBand()
        // .domain(barData.map(d => d.group))
        .domain(barData.map(d => `${d.start}`))
        .rangeRound([0, width])
        .paddingInner(0.2)
      const xScale1 = d3.scaleBand()  // per group
        .domain(perGroup.map(d => d.toString()))
        .rangeRound([0, xScale.bandwidth()])
        .padding(0.05)
      const yScale = d3.scaleLinear()
        .domain([0, yMax])
        .rangeRound([height, 0])
      const xAxis = d3.axisBottom(xScale)
      const yAxis = d3.axisLeft(yScale)
        .ticks(null, 's')
      const svg = d3.select(document.getElementById('recurringtab')).append('svg')
        .attr('id', 'recurringtab-svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
      const g = svg.append('g')
        .attr('id', 'recurring-g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
      g.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(0, ${height})`)
        .call(xAxis)
      g.append('g')
        .attr('class', 'axis')
        .call(yAxis)
      // draw bar chart
      g.selectAll('.recurringtab-bar')
        .data(barData)
        .enter().append('g')
        .attr('transform', d => `translate(${xScale(`${d.start}`)}, 0)`)
        .selectAll('rect')
        .data(d => d.rtptn.map((dd, ii) => {return {key: ii.toString(), val: dd}}))
        .enter().append('rect')
        .attr('x', d => xScale1(d.key))
        .attr('y', d => yScale(d.val))
        .attr('width', xScale1.bandwidth())
        .attr('height', d => height-yScale(d.val))
        .attr('fill', d => colors[+d.key])
    }
  }
}
</script>

<style>
#recurringtab {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
  filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) );
}
</style>
