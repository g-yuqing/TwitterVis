import * as d3 from 'd3'


export default class StreamGraph {
  constructor() {
    this.layerNum = 20
    this.timeNum = 200
    this.init()
  }
  render() {
    const layerNum = this.layerNum,
      sampleNum = this.timeNum,
      stack = d3.stack().keys(d3.range(layerNum).map(d => `layer${d}`).offset(d3.stackOffsetWiggle))
    let matrix = d3.range(sampleNum).map(d => { return {x:d} })
    const layers = stack(matrix)
    const width = 960,
      height = 500
    const xScale = d3.scaleLinear()
      .domain([0, sampleNum-1])
      .range([0, width])
    const yScale = d3.scaleLinear()
      .domain([])
      .range([height, 500])
    const colorScale = d3.scaleSequential(d3.interpolateYlOrRd)
      .domain([0, layerNum])
    const area = d3.area()
      .x(d => xScale(d.data.x))
      .y0(d => yScale(d[0]))
      .y1(d => yScale(d[1]))
    const svg = d3.select('').append('svg')
      .attr('width', width)
      .attr('height', height)
    svg.selectAll('path')
      .data(layers)
      .enter().append('path')
      .attr('d', area)
      .style('fill', (d, i) => colorScale(i))
  }
  update() {

  }
}
