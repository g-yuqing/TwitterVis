import * as d3 from 'd3'


export default class Sunburst{
  constructor(){
  }
  initScene(data) {
    // data: {str: [{str: []}, {term: str, tf: int}]}
    const width = 400,
      height = 300,
      radius = Math.min(width, height)/2-10
    const xScale = d3.scaleLinear()
      .range([0, 2*Math.PI])
    const yScale = d3.scaleSqrt()
      .range([0, radius])

    const partition = d3.partition()
    const arc = d3.arc()
      .startAngle()
      .endAngle()
      .innerRadius()
      .outerRadius()
    const svg = d3.select('topic-sunburst').append('svg')
      .attr('width', width)
      .attr('height', height)
    const g = svg.append('g')
      .attr('transform', `translate(${width/2}, ${height/2})`)
    const root = d3.hierarchy(data)
    root.sum(d => d.tf)

    g.selectAll('path')
      .data(partition(root).descendants())
      .enter().append('path')
      .attr('d', arc)
      .style('fill', '#F00')
      .on('click', click)

    function click(d) {
      svg.Transition()
        .duration(450)
        .tween('scale', function() {
          const xd = d3.interpolate(xScale.domain(), [d.x0, d.x1]),
            yd = d3.interpolate(yScale.domain(), [d.y0, 1]),
            yr = d3.interpolate(yScale.range(), [d.y0?20:0, radius])
          return function(t) {
            xScale.domain(xd(t))
            yScale.domain(yd(t)).range(yr(t))
          }
        })
        .selectAll('path')
        .attrTween('d', function(d) { return function() { return arc(d) } })
    }
  }
}
