import * as d3 from 'd3'
import * as cola from 'webcola'

export default class Topiclayout {
  constructor() {
  }
  initScene(graph) {
    const margin = {top: 70, right: 50, bottom: 10, left:20},
      width = 500,
      height = 500
    // graph.nodes.forEach( d => { d.x = 10, d.y = 10 })
    // graph.links.foreach
    const d3cola = cola.d3adaptor(d3)
      .linkDistance(30)
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
      // .flowLayout('x', 30)
      // .symmetricDiffLinkLengths(6)
      // .jaccardLinkLengths(30,0.7)
      .start(10, 10, 10)
    const link = g.append('g').selectAll('.link')
      .data(graph.links)
      .enter().append('path')
      .attr('stroke', '#bbb')
      .attr('fill', 'none')
    const node = g.append('g').selectAll('.node')
      .data(graph.nodes)
      .enter().append('g')
    // const circle = node.append('circle')
    //   .attr('r', 3)
    //   .style('fill', '#F00')
    //   .on('mouseover', d => {
    //     console.log(d.name)
    //   })
    node.append('text')
      .text(d => d.word)
      .attr('x', 0)
      .attr('y', 3.5)
      .attr('text-anchor', 'middle')
      .attr('fill', d => d.color)
      .style('font-size', '7px')
    d3cola.on('tick', function() {
      // link.attr('d', d => `M${d.target.x},${d.target.y}C${d.target.x},${(d.target.y+d.source.y)/2} ${d.source.x},${(d.target.y+d.source.y)/2} ${d.source.x},${d.source.y}`)
      link.attr('d', d => `M${d.source.x},${d.source.y}
                           L${d.target.x},${d.target.y}`)
        .attr('stroke-linejoin', 'round')
        .attr('stroke-linecap', 'round')
      node.attr('transform', d => `translate(${d.x}, ${d.y})`)
    })
  }
}
