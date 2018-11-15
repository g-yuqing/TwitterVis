import * as d3 from 'd3'
import * as clustering from 'density-clustering'
// import NodeChart from './nodechart'


export default class Statelayout {
  constructor() {
  }
  initScene(graph) {
    this.nodes = graph.nodes
    this.links = graph.links
    const margin = {top: 70, right: 50, bottom: 10, left:20},
      width = 500,
      height = 700-margin.top-margin.bottom,
      graphHeight = height * 0.7,
      colorScale = d3.scaleSequential(d3.interpolateYlOrRd)
        .domain([0, this.nodes.length]),
      sizeScale = d3.scaleLinear()
        .range([3, 10])
        .domain(d3.extent(this.nodes, d => d.ratio))
    const svg = d3.select(document.getElementById('stateview')).append('svg')
      .attr('id', 'state-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const xScale = d3.scaleLinear()
      .range([0, width])
      .domain(d3.extent(this.nodes, d => d.x))
    const yScale = d3.scaleLinear()
      .range([graphHeight, 0])
      .domain(d3.extent(this.nodes, d => d.y))
    const g = svg.append('g')
      .attr('id', 'state-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
    // reset x, y coordinates
    this.nodes.forEach(d => {
      d.x = xScale(d.x)
      d.y = yScale(d.y)
    })
    this.links.forEach(d => {
      d.src.x = xScale(d.src.x)
      d.src.y = yScale(d.src.y)
      d.dst.x = xScale(d.dst.x)
      d.dst.y = yScale(d.dst.y)
    })
    // brush
    const brush = d3.brush()
      .on('start brush', brushed)
      .on('end', brushended)
    function brushed() {
      console.log('selecting')
    }
    function brushended() {
      if(!d3.event.selection) {
        console.log('brushended')
      }
      else {
        const s = d3.event.selection,
          x0 = s[0][0],
          y0 = s[0][1],
          x1 = s[1][0],
          y1 = s[1][1]
        d3.selectAll('.state-node').each(d => {
          if(d.x>=x0 && d.x<=x1 && d.y>=y0 && d.y<=y1) {
            console.log(d.date)
          }
        })
      }
    }
    // links
    const stateLink = g.append('g').selectAll('.link').data(this.links)
      .enter().append('path')
      .attr('id', (d, i) => `state-link${i}`)
      .attr('class', 'state-link')
      .attr('stroke-width', '1.5px')
      .attr('stroke', '#bbb')
      .attr('fill', 'none')
      .attr('d', d => `M${d.src.x},${d.src.y}
                       L${d.dst.x},${d.dst.y}`)
      .on('click', (d, i) => {
        const srcNode = this.nodes[i],
          dstNode = this.nodes[i+1]
        console.log(srcNode.date, dstNode.date)
      })
    // // nodes
    // nodes.forEach((d, i) => {
    //   d.radius = sizeScale(d.ratio)
    //   d.parentNodeColor = colorScale(i)
    //   d.x = xScale(d.x)
    //   d.y = yScale(d.y)
    // })
    // this.stateNode = g.append('g').selectAll('.dot').data(nodes)
    //   .enter().append('g')
    //   .attr('class', 'brush')
    //   .call(brush)
    // this.stateNode.each(function(d) {
    //   const nc = new NodeChart()
    //   nc.drawNodePie(d3.select(this), [], {
    //     parentNodeColor: d.parentNodeColor,
    //     outerStrokeWidth: 5,
    //     radius: d.radius,
    //     showLabelText: false
    //   })
    // })
    // nodes
    const stateNode = g.append('g').selectAll('.dot').data(this.nodes)
      .enter().append('g')
      .attr('class', 'brush')
      .call(brush)
    stateNode.append('circle')
      .attr('id', (d, i) => `state-node${i}`)
      .attr('class', 'state-node')
      .attr('r', d => sizeScale(d.ratio))
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .style('fill', (d, i) => colorScale(i))
    // legend
    // time bar
    const legendWidth = 300,
      legendHeight = 10
    const legendScale = d3.scaleSequential(d3.interpolateYlOrRd)
      .domain([0, legendWidth])
    const timeLegendG = g.append('g')
    timeLegendG.selectAll('.legend')
      .data(d3.range(legendWidth))
      .enter().append('rect')
      .attr('x', d => d)
      .attr('y', graphHeight+margin.top)
      .attr('width', 1)
      .attr('height', 10)
      .style('fill', d => legendScale(d))
    timeLegendG.append('text')
      .attr('class', 'mono')
      .attr('x', 0)
      .attr('y', graphHeight+margin.top+legendHeight*2)
      .style('font-size', '0.5em')
      .style('text-anchor', 'start')
      .text('2011-3-11')
    timeLegendG.append('text')
      .attr('class', 'mono')
      .attr('x', legendWidth)
      .attr('y', graphHeight+margin.top+legendHeight*2)
      .style('font-size', '0.5em')
      .style('text-anchor', 'end')
      .text('2011-12-31')
  }
  // updateNode(valIdxs) {
  //   this.stateNode.each(function(d) {
  //     const nc = new NodeChart()
  //     const arraySum = d3.sum(d.kw)
  //     let percentages = d.kw.filter((d, i) => valIdxs[i] == 1)
  //     percentages = percentages.map(d => d/arraySum)
  //     nc.drawNodePie(d3.select(this), percentages, {
  //       outerStrokeWidth: 5,
  //       radius: d.radius,
  //       showLabelText: false
  //     })
  //   })
  // }
  updateStateView() {
    // clustering
    const margin = {top: 70, right: 50, bottom: 10, left:20},
      width = 500,
      height = 700-margin.top-margin.bottom,
      graphHeight = height * 0.7
    const xScale = d3.scaleLinear()
      .range([0, width])
      .domain([0, this.nodes.length])
    const yScale = d3.scaleLinear()
      .range([graphHeight, 0])
      .domain(d3.extent(this.nodes, d => d.pca))
    d3.selectAll('.state-node')
      .attr('cx', (d, i) => xScale(i))
      .attr('cy', d => yScale(d.pca))
    d3.selectAll('.state-link')
      .attr('d', (d, i) => `M${xScale(i)},${yScale(this.nodes[i].pca)}
                            L${xScale(i+1)},${yScale(this.nodes[i+1].pca)}`)
  }
  resetOriginView() {
    d3.selectAll('.state-node')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
    d3.selectAll('.state-link')
      .attr('d', d => `M${d.src.x},${d.src.y}
                       L${d.dst.x},${d.dst.y}`)
  }
  showClusters() {
    // clustering
    const dbscan = new clustering.DBSCAN()
    const nodepos = this.nodes.map(d => [d.x, d.y])
    const dbclusters = dbscan.run(nodepos, 10, 2)
    const colorScale = d3.scaleSequential(d3.interpolateYlGnBu)
      .domain([0, dbclusters.length])
    const stateHullG = d3.select('#state-g').append('g')
      .selectAll('.hull').data(dbclusters)
      .enter().append('path')
      .attr('class', 'state-hull')
      .attr('d', d => {
        const contours = d.map(d => [this.nodes[d].x, this.nodes[d].y])
        console.log(contours)
        return `M ${contours.join('L')}Z`
      })
      .style('stroke', (d, i) => colorScale(i))
      .style('fill', (d, i) => colorScale(i))
      .style('opacity', 0.7)
      .style('stroke-width', '32px')
      .style('stroke-linejoin', 'round')
  }
}
