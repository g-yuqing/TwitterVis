<template>
  <div id="wormtab">
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
import NodeChart from '../scripts/nodechart'

export default {
  name: 'Wormtab',
  data: () => ({
    tableData: [],
  }),
  mounted() {
    // document.getElementById('wormtab').innerHTML = ''
    this.eventHub.$on('renderWormTab', (data1, data2) => this.drawLineChart(data1, data2))
  },
  watch: {
    tableData(val) {
    },
  },
  methods: {
    drawLineChart(data1, data2) {
      this.tableData = data2
      const width = 500,
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
      let maxValue = 0,
        minValue = 100
      let isVisual = {}
      for(let i=0; i<topics.length; i++) {
        isVisual[topics[i]] = true
      }
      data1.forEach(d => {
        for(const key in d) {
          if(d[key]>maxValue) {
            maxValue = d[key]
          }
          if(d[key]<minValue) {
            minValue = d[key]
          }
        }
      })
      const xScale = d3.scaleTime()
        .domain(d3.extent(data1, d => new Date(d.date)))
        .range([0, width])
      const yScale = d3.scaleLinear()
        .domain([minValue, maxValue+3])
        .range([height, 0])
      const xAxis = d3.axisBottom(xScale)
        .tickFormat(d3.timeFormat('%Y-%m-%d'))
      const yAxis = d3.axisLeft(yScale)
      const svg = d3.select(document.getElementById('wormtab')).append('svg')
        .attr('id', 'wormtab-svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
      svg.append('defs').append('clipPath')
        .attr('id', 'clip')
        .append('rect')
        .attr('width', width)
        .attr('height', height)
      const g = svg.append('g')
        .attr('id', 'wormtab-g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
      g.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(0, ${height})`)
        .call(xAxis)
        .selectAll('text')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em')
        .attr('transform', 'rotate(-65)')
      g.append('g')
        .attr('class', 'axis')
        .call(yAxis)
      // draw linechart
      for(const i in topics) {
        const topic = topics[i]
        const line = d3.line()
          .curve(d3.curveStepBefore)
          .x(d => xScale(new Date(d.date)))
          .y(d => yScale(d[topic]))
        g.append('path')
          .datum(data1)
          .attr('class', 'line')
          .attr('d', line)
          .style('stroke', colors[i])
          .style('stroke-width', 2)
      }
      // draw legend
      const legend = svg.append('svg')
      const legendG = legend.append('g')
        .attr('transform', `translate(${margin.left+10+width}, ${margin.top})`)
      const offset = 30
      for(const i in topics) {
        const topic = topics[i]
        const cell = legendG.append('g')
          .attr('class', 'cell')
          .attr('transform', i<=9 ? `translate(0, ${offset*i})` : `translate(40, ${offset*(i-10)})`)
        cell.append('rect')
          .attr('class', 'legend')
          .attr('width', 35)
          .attr('height', 12)
          .attr('fill', colors[i])
          .on('mouseover', () => {
            d3.selectAll('.line').each(function(dd, ii) {
              if(i!=ii) {
                d3.select(this).style('stroke-opacity', 0)
              }
            })
          })
          .on('mouseleave', () => {
            d3.selectAll('.line').each(function(dd, ii) {
              if(i!=ii) {
                d3.select(this).style('stroke-opacity', 1)
              }
            })
          })
          // .on('click', () => {
          //   if(isVisual[topic]) {
          //     isVisual[topic] = false
          //     d3.selectAll('.line').each(function(dd, ii) {
          //       if(i == ii) {
          //         d3.select(this).style('stroke-opacity', 0)
          //       }
          //     })
          //   }
          //   else {
          //     isVisual[topic] = true
          //     d3.selectAll('.line').each(function(dd, ii) {
          //       if(i == ii) {
          //         d3.select(this).style('stroke-opacity', 1)
          //       }
          //     })
          //   }
          // })
          cell.append('text')
            .attr('class', 'label')
            .attr('transform', 'translate(0, 25)')
            .text(topics[i].split('_').join('&'))
      }

      // // data1 is required to be
      // // [[{date, rtptn, rate}, {}], [{date, rtptn, rate}, {}]]
      // console.log(data2);
      // this.tableData = data2
      // const width = 900,
      //   height = 70,
      //   margin = {top: 30, right: 70, bottom: 50, left:70},
      //   colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
      //     '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',
      //     '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000',
      //     '#ffd8b1', '#000080', '#808080', '#FFFFFF', '#000000'],
      //   topics = ['原発_稼働', '原発_東電', '原発_福島',
      //     '放射能_福島', '福島_避難', '原発_報道',
      //     '報道_福島', '安全_福島', '福島_被曝',
      //     '事故_原発', '原発_安全', '原発_電力',
      //     '復興_福島', '国民_東電', '東電_福島',
      //     '子供_福島', '政府_東電', '東電_社員',
      //     '原発_反対', '影響_福島']
      // const sizeScale = d3.scaleLinear()
      //     .range([10, 25])
      //     .domain(d3.extent(data1, d => d.rate))
      // const svg = d3.select(document.getElementById('wormtab')).append('svg')
      //     .attr('id', 'wormtab-svg')
      //     .attr('width', width + margin.left + margin.right)
      //     .attr('height', height + margin.top + margin.bottom)
      // const g = svg.append('g')
      //     .attr('id', 'wormtab-g')
      //     .attr('transform', `translate(${margin.left}, ${margin.top})`)
      // const xScale = d3.scaleTime()
      //     .domain(d3.extent(data1, d => new Date(d.date)))
      //     .range([0, width])
      // const xAxis = d3.axisBottom(xScale)
      //     .tickFormat(d3.timeFormat('%Y-%m-%d'))
      // g.append('g')
      //     .attr('class', 'axis')
      //     .attr('transform', `translate(0, ${height})`)
      //     .call(xAxis)
      //     .selectAll('text')
      //     .style('text-anchor', 'end')
      //     .attr('dx', '-.8em')
      //     .attr('dy', '.10em')
      //     .attr('font-size', '7px')
      //     .attr('transform', 'rotate(-65)')
      // const wormNode = g.append('g').selectAll('.dot').data(data1)
      //     .enter().append('g')
      // wormNode.each(function(d, i) {
      //     const nc = new NodeChart()
      //     const temp = []
      //     for(const i in d.rtptn) {
      //       temp.push({color: i, percent: d.rtptn[i] * 100})
      //     }
      //     nc.drawNodePie(d3.select(this), temp, {
      //       outerStrokeWidth: 5,
      //       radius: sizeScale(d.rate),
      //       showLabelText: false,
      //       circleClass: 'worm-circle'
      //     })
      //   })
      // d3.selectAll('.worm-circle')
      //   .attr('cx', dd => xScale(new Date(dd.date)))
      //   .attr('cy', height)
    }
  }
}
</script>

<style>
#wormtab {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
  filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) );
}
.line {
    fill: none;
    stroke-width: 1px;
    clip-path: url(#clip);
}
.label {
    font-size: 7px;
}
</style>
