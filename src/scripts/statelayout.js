import * as d3 from 'd3'
import NodeChart from './nodechart'


export default class Statelayout {
  constructor() {
    this.colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
      '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',
      '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000',
      '#ffd8b1', '#000080', '#808080', '#FFFFFF', '#000000']
  }
  initScene(graph) {
    const margin = {top: 70, right: 50, bottom: 10, left:20},
      width = 500,
      height = 700-margin.top-margin.bottom,
      graphHeight = height * 0.7,
      nodes = graph.nodes,
      links = graph.links,
      clusters = graph.clusters,
      colorScale = d3.scaleSequential(d3.interpolateYlOrRd)
        .domain([0, nodes.length]),
      colorScaleState = ['#007AFF', '#28CD41', '#FF2D55', '#FFCD00'],
      sizeScale = d3.scaleLinear()
        .range([5, 15])
        .domain(d3.extent(nodes, d => d.ratio))
    const svg = d3.select(document.getElementById('stateview')).append('svg')
      .attr('id', 'state-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const xScale = d3.scaleLinear()
      .range([0, width])
      .domain(d3.extent(nodes, d => d.x))
    const yScale = d3.scaleLinear()
      .range([graphHeight, 0])
      .domain(d3.extent(nodes, d => d.y))
    const g = svg.append('g')
      .attr('id', 'state-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
    // hull
    const stateHullG = g.append('g')
      .attr('id', 'state-hull')
    stateHullG.selectAll('.hull').data(clusters)
      .enter().append('path')
      .attr('class', 'hull')
      .attr('d', d => {
        let contours
        if(d.npos.length >= 3) {
          contours = d.npos.map(d => [xScale(d[0]), yScale(d[1])])
          // contours = d3.polygonHull(d.npos.map(d => [xScale(d[0]), yScale(d[1])]))
        }
        else {
          contours = d.npos.map(d => [xScale(d[0]), yScale(d[1])])
        }
        return `M ${contours.join('L')}Z`
      })
      .style('stroke', d => colorScaleState[d.state])
      .style('fill', d => colorScaleState[d.state])
    // links
    const stateLink = g.append('g').selectAll('.link').data(links)
      .enter().append('path')
      .attr('id', (d, i) => `state-path${i}`)
      .attr('stroke', '#bbb')
      .attr('fill', 'none')
      .attr('d', d => `M${xScale(d.src.x)},${yScale(d.src.y)}
                       L${xScale(d.dst.x)},${yScale(d.dst.y)}`)
      .on('mouseover', d => {
        console.log(d)
      })
    // nodes
    const stateNode = g.append('g').selectAll('.dot').data(nodes)
      .enter().append('circle')
      .attr('r', d => sizeScale(d.ratio))
      .attr('cx', d => xScale(d.x))
      .attr('cy', d => yScale(d.y))
      .style('fill', (d, i) => colorScale(i))
      // .style('fill', d => colorScaleCluster(d.clu))
      .on('mouseover', d => {
        console.log(d)
      })
    //   .enter().append('g')
    // stateNode.each(function(d, i) {
    //   const nc = new NodeChart()
    //   const temp = []
    //   for(const i in d.rtptn) {
    //     temp.push({color: i, percent: d.rtptn[i] * 100})
    //   }
    //   nc.drawNodePie(d3.select(this), temp, {
    //     parentNodeColor: colorScale(i),
    //     outerStrokeWidth: 5,
    //     radius: sizeScale(d.ratio),
    //     showLabelText: false
    //   })
    // })
    // d3.selectAll('circle')
    //   .attr('cx', d => xScale(d.x))
    //   .attr('cy', d => yScale(d.y))
    //   .on('mouseover', d => {
    //     console.log(d)
    //   })

    // // legend
    // // time bar
    // const legendWidth = 300,
    //   legendHeight = 10
    // const legendScale = d3.scaleSequential(d3.interpolateYlOrRd)
    //   .domain([0, legendWidth])
    // const timeLegendG = g.append('g')
    // timeLegendG.selectAll('.legend')
    //   .data(d3.range(legendWidth))
    //   .enter().append('rect')
    //   .attr('x', d => d)
    //   .attr('y', graphHeight+margin.top)
    //   .attr('width', 1)
    //   .attr('height', 10)
    //   .style('fill', d => legendScale(d))
    // timeLegendG.append('text')
    //   .attr('class', 'mono')
    //   .attr('x', 0)
    //   .attr('y', graphHeight+margin.top+legendHeight*2)
    //   .style('font-size', '0.5em')
    //   .style('text-anchor', 'start')
    //   .text('2011-3-11')
    // timeLegendG.append('text')
    //   .attr('class', 'mono')
    //   .attr('x', legendWidth)
    //   .attr('y', graphHeight+margin.top+legendHeight*2)
    //   .style('font-size', '0.5em')
    //   .style('text-anchor', 'end')
    //   .text('2016-12-31')

    // zoom event
    const zoomHander = d3.zoom()
      .on('zoom', zoomActions)
    function zoomActions() {
      stateNode.attr('transform', d3.event.transform)
      stateLink.attr('transform', d3.event.transform)
      stateHullG.attr('transform', d3.event.transform)
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
    //   stateNode.style('opacity', d => {
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
  periodicView() {
    function colorScale1(dateinfo){
      const ymd = dateinfo.split('-')
      return `hsl(${(ymd[1]-2011)*20}, 100%, 50%)`
    }
    d3.select('#state-g').selectAll('circle')
      .style('fill', d => colorScale1(d.date))
  }

}
