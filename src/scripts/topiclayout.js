import * as d3 from 'd3'
import * as cola from 'webcola'

export default class Topiclayout {
  constructor() {
  }
  initScene(graph) {
    const margin = {top: 70, right: 50, bottom: 10, left:20},
      width = 700,
      height = 300
    const d3cola = cola.d3adaptor(d3)
      .avoidOverlaps(true)
      .size([width, height])

    const fontScale = d3.scaleLinear()
      .range([7,15])
      .domain(d3.extent(graph.nodes, d => d.tf))

    const svg = d3.select(document.getElementById('topicview')).append('svg')
      .attr('id', 'topic-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const g = svg.append('g')
      .attr('id', 'topic-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
    d3cola.nodes(graph.nodes)
      .links(graph.links)
      .constraints(graph.constraints)
      .flowLayout('x', 15)
      .symmetricDiffLinkLengths(10)
      // .jaccardLinkLengths(40,0.7)
      .start(10, 20, 20)
    const link = g.append('g').selectAll('.link')
      .data(graph.links)
      .enter().append('path')
      .attr('stroke', '#A8A7A7')
      .attr('fill', 'none')
      .style('stroke-opacity', 0.5)
    const node = g.append('g').selectAll('.node')
      .data(graph.nodes)
      .enter().append('g')
    node.append('text')
      .text(d => d.word)
      .attr('x', 0)
      .attr('y', 3.5)
      .attr('text-anchor', 'middle')
      .attr('fill', d => d.color)
      .style('font-size', d => `${fontScale(d.tf)}px`)
    d3cola.on('tick', function() {
      link.attr('d', d => `M${d.target.x},${d.target.y}C${d.target.x},${(d.target.y+d.source.y)/2} ${d.source.x},${(d.target.y+d.source.y)/2} ${d.source.x},${d.source.y}`)
      node.attr('transform', d => `translate(${d.x}, ${d.y})`)
    })
  }
}
