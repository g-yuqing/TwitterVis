<template>
  <div id="textlayout"></div>
</template>

<script>
import * as d3 from 'd3'

export default {
  name: 'Textlayout',
  data() {
    return {
    }
  },
  mounted() {
    // this.render('../../static/current/text_pre_visualize.json')
    this.render('../../static/current/text_post_visualize.json')
  },
  methods: {
    render(filepath) {
      const margin = {top: 30, right: 50, bottom: 10, left:20},
        width = 600,
        height = 560
      d3.json(filepath).then(dataset => {
        console.log(dataset);
        const nodes = dataset.nodes
        const colorScale = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
          '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',
          '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000',
          '#ffd8b1', '#000080', '#808080', '#FFFFFF', '#000000']
        // const colorScale = d3.scaleSequential(d3.interpolateYlOrRd)
        //     .domain([0, nodes.length])
        const svg = d3.select(document.getElementById('textlayout')).append('svg')
              .attr('id', 'text-svg')
              .attr('width', width + margin.left + margin.right)
              .attr('height', height + margin.top + margin.bottom)
        const xScale = d3.scaleLinear()
          .range([0, width])
          .domain(d3.extent(nodes, d => d.x))
        const yScale = d3.scaleLinear()
          .range([height, 0])
          .domain(d3.extent(nodes, d => d.y))
        const g = svg.append('g')
          .attr('id', 'text-g')
          .attr('transform', `translate(${margin.left}, ${margin.top})`)
        // nodes
        const textNode = g.selectAll('.dot').data(nodes)
          .enter().append('circle')
          .attr('r', 3)
          .attr('cx', d => xScale(d.x))
          .attr('cy', d => yScale(d.y))
          .style('fill', (d, i) => colorScale[d.c])
          .on('mouseover', d => {
              console.log(d)
          })
      })
    }
  }
}
</script>

<style>
  .dot {
    /* stroke: #000; */
  }
  .axis--grid .domain {
    fill: #ddd;
    stroke: none;
  }
  .axis--x .domain,
  .axis--grid .tick line {
    stroke: #fff;
  }
  .axis--grid .tick--minor line {
    stroke-opacity: 0.5;
  }
  .brush .selection {
    fill: steelblue;
  }
  #tsnelayout {
    -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
    filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) )
  }
</style>
