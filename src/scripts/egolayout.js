import * as d3 from 'd3'


export default function drawEgolayout(graph) {
  document.getElementById('egolayout').innerHTML = ''
  const margin = {top: 30, right: 120, bottom: 10, left:30},
    padHeight = 20,
    width = 400,
    height = 400,
    nodes = graph.nodes,
    edges = graph.edges

  const xScale = d3.scaleLinear()
    .domain(d3.extent(nodes, d => d.x))
    .range([0, width])
  const yScale = d3.scaleLinear()
    .domain(d3.extent(nodes, d => d.y))
    .range([height, 0])
  const sizeScale = d3.scaleLinear()
    .domain(d3.extent(nodes, d => d.size))
    .range([3, 10])

  const svg = d3.select(document.getElementById('egolayout')).append('svg')
    .attr('width', width+margin.left+margin.right)
    .attr('height', height+margin.top+margin.bottom)

  const group = svg.append('g')
    .attr('id', 'ego-g')
    .attr('transform', `translate(${margin.left}, ${margin.top})`)
  const link = group.append('g')
    .attr('class', 'ego-edges')
    .selectAll('.egoline')
    .data(edges)
    .enter().append('line')
    .attr('x1', d => xScale(d.src.x))
    .attr('y1', d => yScale(d.src.y))
    .attr('x2', d => xScale(d.dst.x))
    .attr('y2', d => yScale(d.dst.y))
  const node = group.append('g')
    .attr('class', 'ego-nodes')
    .selectAll('.ego-nodes')
    .data(nodes)
    .enter().append('circle')
    .attr('r', d => sizeScale(d.size))
    .attr('cx', d => xScale(d.x))
    .attr('cy', d => yScale(d.y))
    .attr('fill', (d,i) => i==0?'#3cb44b':'steelblue')
    .on('mouseover', d => {
      d3.select('#ego_text_g').remove()
      const text_g = svg.append('g')
        .attr('id', 'ego_text_g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
      const padText = text_g.selectAll('.nodeText')
        .data([d])
      padText.enter().append('text')
        .text(dd => `retweeted count: ${dd.size}`)
        .attr('x', dd => xScale(dd.x)+10)
        .attr('y', dd => yScale(dd.y)-10)
        .style('text-anchor', 'start')
        .style('font-size', '0.7em')
    })
    .on('mouseleave', () => d3.select('#ego_text_g').remove())
}
