import * as d3 from 'd3'
import * as cola from 'webcola'

export default class Topiclayout {
  constructor() {
  }
  initScene(graph) {
    const margin = {top: 70, right: 50, bottom: 10, left:20},
      width = 1200,
      height = 500
    graph.nodes.forEach( d => { d.x = 10, d.y = 10 })
    graph.links.foreach
    const d3cola = cola.d3adaptor(d3)
      .linkDistance(120)
      .avoidOverlaps(true)
      .size([width, height])
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
      .flowLayout('x', 5)
      .symmetricDiffLinkLengths(5)
      .start(10, 10, 10)
    const link = g.append('g').selectAll('.link')
      .data(graph.links)
      .enter().append('line')
      .attr('class', 'link')
      .style('stroke', '#999')
      .style('stroke-width', 1)
    const node = g.append('g').selectAll('.node')
      .data(graph.nodes)
      .enter().append('g')
    const circle = node.append('circle')
      .attr('r', 3)
      .style('fill', '#F00')
      .on('mouseover', d => {
        console.log(d.name)
      })
    node.append('text')
      .text(d => d.word)
      .attr('x', 6)
      .attr('y', 3)
      .style('font-size', '7px')
    d3cola.on('tick', function() {
      link.attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)
      // node.attr('cx', d => d.x)
      //   .attr('cy', d => d.y)
      node.attr('transform', d => `translate(${d.x}, ${d.y})`)
    })
  }
}
