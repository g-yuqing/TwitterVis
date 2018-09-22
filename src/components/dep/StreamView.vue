<template>
  <div id="streamgraph"></div>
</template>

<script>
import * as d3 from 'd3'

export default {
  name: 'Streamgraph',
  data() {
    return {
    }
  },
  mounted() {
    this.eventHub.$on('initStreamgraph', dataset => this.renderScene(dataset))
  },
  methods: {
    renderScene(dataset) {
      const nodes = dataset.nodes
      const n = nodes[0].c.length, // number of layers
        m = nodes.length, // number of samples per layer
        stack = d3.stack().keys(d3.range(n).map(function (d) { return "layer"+d; })).offset(d3.stackOffsetWiggle)

      // Create empty data structures
      // const matrix0 = d3.range(m).map(function (d) { return { x:d } })
      // // Fill them with random data
      // d3.range(n).map(function(d) { bumpLayer(m, matrix0, d) })
      let matrix0 = []
      for(let i=0;i<m;i++) {
        matrix0[i] = {x:i}
        for(let j=0;j<n;j++) {
            matrix0[i][`layer${j}`] = nodes[i]['c'][j]
        }
      }

      const layers0 = stack(matrix0)

      const width = window.innerWidth,
        height = 500


      const x = d3.scaleLinear()
          .domain([0, m - 1])
          .range([0, width]);

      const y = d3.scaleLinear()
          .domain([d3.min(layers0, function(layer) { return d3.min(layer, function(d) { return d[0]; }); }), d3.max(layers0, function(layer) { return d3.max(layer, function(d) { return d[1]; }); })])
          .range([height, 0])


      const colorScale = d3.scaleOrdinal(d3.schemeCategory10)


      const area = d3.area()
          .x(function(d,i) { return x(d.data.x) })
          .y0(function(d) { return y(d[0]) })
          .y1(function(d) { return y(d[1]) })

      const svg = d3.select(document.getElementById('streamgraph')).append('svg')
          .attr("width", width)
          .attr("height", height)


      svg.selectAll("path")
          .data(layers0)
        .enter().append("path")
          .attr("d", area)
          .style("fill", (d, i) => colorScale(i))

    // x axis
    const xScale = d3.scaleTime()
      .domain([new Date(2011, 2, 1), new Date(2017, 0, 1)-1])
      .rangeRound([0, width]);
    svg.append("g")
      .attr("transform", `translate(0,0)`)
      .call(d3.axisTop()
        .scale(xScale)
        .ticks(d3.timeMonth)
        .tickSize(-10)
        .tickFormat(d3.timeFormat('%y/%m')))
          .selectAll('text')
          .style('text-anchor', 'end')
          .attr('dx', '-.8em')
          .attr('dy', '.15em')
          .attr('transform', 'rotate(-65)')


    }
  }
}
</script>

<style>
</style>
