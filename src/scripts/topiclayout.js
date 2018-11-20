import * as d3 from 'd3'
import * as cola from 'webcola'

export default class Topiclayout {
  constructor() {
  }
  initScene(graph) {
    const margin = {top: 20, right: 10, bottom: 50, left:20},
      width = document.getElementById('topicview').offsetWidth-margin.left-margin.right,
      height = document.getElementById('topicview').offsetHeight-margin.top-margin.bottom
    const fontScale = d3.scaleLinear()
      .range([7,15])
      .domain(d3.extent(graph.nodes, d => d.tf))
    const xScale = d3.scaleLinear()
      .range([0, width])
    const yScale = d3.scaleLinear()
      .range([height, 0])
    // empty previous visualization
    document.getElementById('topicview').innerHTML = ''
    // visualize
    const svg = d3.select(document.getElementById('topicview')).append('svg')
      .attr('id', 'topic-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const g = svg.append('g')
      .attr('id', 'topic-g')
      .attr('width', width)
      .attr('height', height)
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
    const d3cola = cola.d3adaptor(d3)
      .avoidOverlaps(true)
      // .flowLayout('x', 25)
      .size([width, height])
      .nodes(graph.nodes)
      .links(graph.links)
      .constraints(graph.constraints)
      .symmetricDiffLinkLengths(25)
      // .jaccardLinkLengths(30,0.7)
      .start(10, 20, 20)
      // .start(10, 40, 80)
    const link = g.append('g').selectAll('.link')
      .data(graph.links)
      .enter().append('path')
      .attr('class', 'topic-link')
      .attr('stroke', '#A8A7A7')
      .attr('fill', 'none')
      .style('stroke-opacity', 0.2)
    // const node = g.append('g').selectAll('.node')
    //   .data(graph.nodes)
    //   .enter().append('g')
    // node.append('text')
    //   .text(d => d.word)
    //   .attr('x', 0)
    //   .attr('y', 3.5)
    //   .attr('text-anchor', 'middle')
    //   .attr('fill', d => d.color)
    //   .style('font-size', d => `${fontScale(d.tf)}px`)
    // d3cola.on('tick', function() {
    //   link.attr('d', d => `M${d.target.x},${d.target.y}C${d.target.x},${(d.target.y+d.source.y)/2} ${d.source.x},${(d.target.y+d.source.y)/2} ${d.source.x},${d.source.y}`)
    //   node.attr('transform', d => `translate(${d.x}, ${d.y})`)
    // })
    graph.nodes.forEach(d => {
      d.width = 10*d.word.length,
      d.height = 10
    })
    const node = g.append('g').selectAll('.node')
      .data(graph.nodes)
      .enter().append('rect')
      .attr('class', 'topic-node')
      .attr('width', d => d.width)
      .attr('height', d => d.height)
      .style('fill', 'none')
    d3cola.on('tick', function() {
      xScale.domain(d3.extent(graph.nodes, d => d.x))
      yScale.domain(d3.extent(graph.nodes, d => d.y))
      link.attr('d', d => `M${xScale(d.source.x)},${yScale(d.source.y)}L${xScale(d.target.x)},${yScale(d.target.y)}`)
      node.attr('x', d => xScale(d.x-d.width/2))
        .attr('y', d => yScale(d.y-d.height/2))
    })

  }
}
