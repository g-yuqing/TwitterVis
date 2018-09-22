import * as d3 from 'd3'
import NodeChart from './nodechart'


export default class Mdslayout {
  constructor() {
    this.colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
      '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',
      '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000',
      '#ffd8b1', '#000080', '#808080', '#FFFFFF', '#000000']
  }
  initScene(dataset) {
    // function genDatelist(startDate, endDate) {
    //   const datelist = []
    //   let currentDate = startDate
    //   while(currentDate<endDate) {
    //     datelist.push(currentDate)
    //     const m = currentDate.getMonth()+1,
    //       y = currentDate.getFullYear()
    //     currentDate = new Date(y, m)
    //   }
    //   return datelist
    // }
    const margin = {top: 30, right: 50, bottom: 10, left:20},
      width = 600,
      height = 800,
      graphHeight = height * 0.7,
      // sliderHeight = 20,
      nodes = dataset.nodes,
      links = dataset.links,
      // startDate = new Date(2011, 0, 1),
      // endDate = new Date(2013, 0, 1),
      // datelist = genDatelist(startDate, endDate),
      colorScale = d3.scaleSequential(d3.interpolateYlOrRd)
        .domain([0, nodes.length])
    const svg = d3.select(document.getElementById('tsnelayout')).append('svg')
      .attr('id', 'tsne-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const xScale = d3.scaleLinear()
      .range([0, width])
      .domain(d3.extent(nodes, d => d.x))
    const yScale = d3.scaleLinear()
      .range([graphHeight, 0])
      .domain(d3.extent(nodes, d => d.y))
    const g = svg.append('g')
      .attr('id', 'tsne-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
    // links
    const tsneLink = g.selectAll('.link').data(links)
      .enter().append('path')
      .attr('stroke', '#bbb')
      .attr('fill', 'none')
      .attr('d', d => `M${xScale(d.src.x)},${yScale(d.src.y)}
                       L${xScale(d.dst.x)},${yScale(d.dst.y)}`)
    // // nodes
    const tsneNode = g.selectAll('.dot').data(nodes)
      // .enter().append('circle')
      // .attr('r', 3)
      // .attr('cx', d => xScale(d.x))
      // .attr('cy', d => yScale(d.y))
      // .style('fill', (d, i) => colorScale(i))
      // .on('mouseover', d => {
      //   console.log(d.d)
      // })
      .enter().append('g')
    tsneNode.each(function(d, i) {
      const nc = new NodeChart()
      const temp = []
      for(const i in d.c) {
        temp.push({color: i, percent: d.c[i] * 100})
      }
      nc.drawNodePie(d3.select(this), temp, {parentNodeColor: colorScale(i), outerStrokeWidth: 5, showLabelText: false})
    })
    d3.selectAll('circle')
      .attr('cx', d => xScale(d.x))
      .attr('cy', d => yScale(d.y))
      .on('mouseover', d => {
        console.log(d.d)
      })

    // zoom event
    const zoomHander = d3.zoom()
      .on('zoom', zoomActions)
    function zoomActions() {
      tsneNode.attr('transform', d3.event.transform)
      tsneLink.attr('transform', d3.event.transform)
    }
    zoomHander(svg)

    // // add time slider
    // const tXScale = d3.scaleTime()
    //   .domain([new Date(2011, 0, 1), new Date(2013, 0, 1)-1])
    //   .rangeRound([0, width])
    // const sliderG = svg.append('g')
    //   .attr('id', 'slider-g')
    //   .attr('transform', `translate(${margin.left}, ${graphHeight+margin.top+60})`)
    // sliderG.append('g')
    //   .attr('class', 'axis axis--grid')
    //   .attr('transform', `translate(0, ${sliderHeight})`)
    //   .call(d3.axisBottom()
    //     .scale(tXScale)
    //     .ticks(d3.timeMonth)
    //     .tickSize(-sliderHeight)
    //     .tickFormat(d3.timeFormat('%y/%m')))
    //   .selectAll('text')
    //   .style('text-anchor', 'end')
    //   .attr('dx', '-.8em')
    //   .attr('dy', '.15em')
    //   .attr('transform', 'rotate(-65)')
    // sliderG.append('g')
    //   .attr('class', 'brush')
    //   .call(d3.brushX()
    //     .extent([[0, 0], [width, sliderHeight]])
    //     .on('end', brushended)
    //   )
    // function brushended() {
    //   if (!d3.event.sourceEvent) return // Only transition after input.
    //   if (!d3.event.selection) return // Ignore empty selections.
    //   const d0 = d3.event.selection.map(tXScale.invert),
    //     d1 = d0.map(d3.timeMonth.round)
    //   if (d1[0] >= d1[1]) {
    //     d1[0] = d3.timeMonth.floor(d0[0])
    //     d1[1] = d3.timeMonth.offset(d1[0])
    //   }
    //   d3.select(this).transition().call(d3.event.target.move, d1.map(tXScale))
    //   // hide unselected nodes
    //   tsneNode.style('opacity', d => {
    //     for(let i=0;i<d.rtd.length;i++) {
    //       if(d.rtd[i]>=100) {
    //         if(d1[0]<=datelist[i] && datelist[i]<d1[1]) {
    //           return 1
    //         }
    //       }
    //     }
    //     return 0
    //   })
    // }
  }
  updateScene() {

  }
}
