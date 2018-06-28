import * as d3 from 'd3'


export default function drawTimeline(dataset) {
  document.getElementById('timeline').innerHTML = ''
  const parseTime = d3.timeParse('%Y-%m-%d')
  dataset.forEach(d => {
    d.date = parseTime(d.date)
  })
  const margin = {top: 30, right: 30, bottom: 10, left:30},
    padHeight = 20,
    width = 1200,
    height = 100

  const colorScale = d3.scaleSequential(d3.interpolateInferno)
    .domain(d3.extent(dataset, d => d.count).reverse())
  const xScale = d3.scaleTime()
    .domain(d3.extent(dataset, d => d.date))
    .range([0, width])
  // const xAxis = d3.axisBottom()
  const xAxis = d3.axisTop()
    .scale(xScale)
    .tickFormat(d3.timeFormat('%Y-%m-%d'))

  const svg = d3.select(document.getElementById('timeline')).append('svg')
    .attr('width', width+margin.left+margin.right)
    .attr('height', height+margin.top+margin.bottom)

  const group = svg.append('g')
    .attr('id', 'timeline-g')
    .attr('transform', `translate(${margin.left}, ${margin.top})`)
  group.append('g')
    .attr('class', 'x axis')
    .attr('transform', 'translate(0, 0)')
    .call(xAxis)
    .selectAll('text')
    .style('text-anchor', 'middle')
    .attr('dx', '-.8em')
    .attr('dy', '.15em')
    .attr('transform', 'rotate(35)')

  group.selectAll('.pad').append('g').data(dataset)
    .enter().append('rect')
    .attr('x', d => xScale(d.date))
    .attr('y', 10)
    .attr('width', 10)
    .attr('height', padHeight)
    .style('fill', d => d.count==0?'none':colorScale(d.count))
    .on('mouseover', d => {
      d3.select('#text_g').remove()
      const text_g = svg.append('g')
        .attr('id', 'text_g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
      const padText = text_g.selectAll('.gridText')
        .data([d])
      padText.enter().append('text')
        .text(dd => `${dd.count}`)
        .attr('x', dd => xScale(dd.date))
        .attr('y', 20+margin.top)
        .style('text-anchor', 'start')
        .style('font-size', '0.7em')
      // console.log(d)
    })
    .on('mouseleave', () => d3.select('#text_g').remove())
}
