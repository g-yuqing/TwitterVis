import * as d3 from 'd3'
import _ from 'lodash'
import Keywordlayout from './keywordlayout'


export default class Statelayout {
  constructor() {
  }
  initScene(stateData, keywordData) {
    // stateData: {nodes: [{}, {}], links: []}
    // keywordData: [{date: date, kwscore: []}, {}, {}]
    document.getElementById('stateview').innerHTML = ''
    this.nodes = _.cloneDeep(stateData.nodes)
    this.links = _.cloneDeep(stateData.links)
    const margin = {top: 70, right: 50, bottom: 10, left:50},
      width = document.getElementById('stateview').offsetWidth-margin.right-margin.left,
      height = document.getElementById('stateview').offsetHeight-margin.top-margin.bottom,
      graphHeight = height * 0.8,
      dateHull = {},
      kl = new Keywordlayout()
    // ============================ init stateview ============================
    // graph + legend
    const colorScale = d3.scaleSequential(d3.interpolateYlOrRd)
        .domain([0, this.nodes.length]),
      sizeScale = d3.scaleLinear()
        .range([3, 10])
        .domain(d3.extent(this.nodes, d => d.ratio))
    const xScale = d3.scaleLinear()
      .range([0, width])
      .domain(d3.extent(this.nodes, d => d.x))
    const yScale = d3.scaleLinear()
      .range([graphHeight, 0])
      .domain(d3.extent(this.nodes, d => d.y))
    const xScalePCA = d3.scaleBand()
      .range([0, width])
      .domain(this.nodes.map(d => d.date))
    const yScalePCA = d3.scaleLinear()
      .range([graphHeight, 0])
      .domain(d3.extent(this.nodes, d => d.pca))
    // reset x, y coordinates
    this.nodes.forEach(d => {
      d.x = xScale(d.x)
      d.y = yScale(d.y)
      // pca
      d.px = xScalePCA(d.date)
      d.py = yScalePCA(d.pca)
    })
    this.links.forEach((d, i) => {
      d.src.x = xScale(d.src.x)
      d.src.y = yScale(d.src.y)
      d.dst.x = xScale(d.dst.x)
      d.dst.y = yScale(d.dst.y)
      // pca
      d.src.px = this.nodes[i].px
      d.src.py = this.nodes[i].py
      d.dst.px = this.nodes[i+1].px
      d.dst.py = this.nodes[i+1].py
    })
    const svg = d3.select(document.getElementById('stateview')).append('svg')
      .attr('id', 'stateview-svg')
      .attr('width', width+margin.right+margin.left)
      .attr('height', height+margin.top+margin.bottom)
    const g = svg.append('g')
      .attr('id', 'stateview-g')
      .attr('width', width)
      .attr('height', height)
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
    // brush
    const brush = d3.brush()
      .on('end', brushended)
    // hulls
    const hullColor = ['#99B898', '#FECEAB', '#FF847C', '#E84A5F']
    const temp = {},
      temp1 = {},
      temp2 = {}
    for(const node of this.nodes) {
      const group = node.g,
        x = node.x,
        y = node.y,
        px = node.px,
        py = node.py,
        state = node.state
      temp[group] = state
      if(group in temp1) {
        temp1[group].push([x, y])
        temp2[group].push([px, py])
      }
      else {
        temp1[group] = [[x, y]]
        temp2[group] = [[px, py]]
      }
      // init dateHull
      dateHull[node.date] = {
        group: node.g,
        state: node.state
      }
    }
    const hull = []  // [{group: nodes}]
    for(const key in temp) {
      hull.push({
        group: key,
        state: temp[key],
        nodes: temp1[key],
        pnodes: temp2[key]
      })
    }
    g.append('g').selectAll('.hull').data(hull)
      .enter().append('path')
      .attr('class', 'stateview-hull')
      .attr('d', d => `M ${d.nodes.join('L')}Z`)
      .style('stroke', d => hullColor[+d.state])
      .style('fill', d => hullColor[+d.state])
      .style('stroke-width', '20px')
      .style('stroke-linejoin', 'round')
      .style('opacity', 0)
    // links
    g.append('g').selectAll('.link').data(this.links)
      .enter().append('path')
      .attr('class', 'stateview-link')
      .attr('id', (d, i) => `stateview-link${i}`)
      .attr('stroke-width', '1.5px')
      .attr('stroke', '#A8A7A7')
      .attr('fill', 'none')
      .attr('d', d => `M${d.src.x},${d.src.y}
                       L${d.dst.x},${d.dst.y}`)
    // nodes
    const stateNode = g.append('g').selectAll('.dot').data(this.nodes)
      .enter().append('g')
      .attr('class', 'brush')
      .call(brush)
    stateNode.append('circle')
      .attr('class', 'stateview-node')
      .attr('id', (d, i) => `stateview-node${i}`)
      .attr('r', d => sizeScale(d.ratio))
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .style('fill', (d, i) => colorScale(i))
    // legend
    const legendMargin = {top: 20},
      legendWidth = 300,
      legendHeight = 10
    const legendScale = d3.scaleSequential(d3.interpolateYlOrRd)
      .domain([0, legendWidth])
    const timeLegendG = g.append('g')
      .attr('class', 'stateview-legend')
    timeLegendG.selectAll('.legend')
      .data(d3.range(legendWidth))
      .enter().append('rect')
      .attr('class', 'stateview-legend-rect')
      .attr('x', d => d)
      .attr('y', graphHeight+legendMargin.top)
      .attr('width', 1)
      .attr('height', 10)
      .style('fill', d => legendScale(d))
    timeLegendG.append('text')
      .attr('class', 'stateview-text')
      .attr('x', 0)
      .attr('y', graphHeight+legendMargin.top+legendHeight*2)
      .style('font-size', '0.5em')
      .style('text-anchor', 'start')
      .text(this.nodes[0].date)
    timeLegendG.append('text')
      .attr('class', 'stateview-text')
      .attr('x', legendWidth)
      .attr('y', graphHeight+legendMargin.top+legendHeight*2)
      .style('font-size', '0.5em')
      .style('text-anchor', 'end')
      .text(this.nodes[this.nodes.length-1].date)
      // .text('2011-12-31')
    function brushended() {
      if(d3.event.selection) {
        const data = []
        const s = d3.event.selection,
          x0 = s[0][0],
          y0 = s[0][1],
          x1 = s[1][0],
          y1 = s[1][1]
        d3.selectAll('.stateview-node').each(d => {
          if(d.x>=x0 && d.x<=x1 && d.y>=y0 && d.y<=y1) {
            data.push({
              date: d.date,
              kwscore: keywordData.period[d.date]
            })
          }
        })
        if(data.length != 0) {
          kl.initScene(data, dateHull)
        }
      }
    }
  }
  switchDimension(opt) {
    if(opt) {  // one dimension
      d3.selectAll('.stateview-link')
        .attr('d', d => `M${d.src.px},${d.src.py}
                         L${d.dst.px},${d.dst.py}`)
      d3.selectAll('.stateview-node')
        .attr('cx', d => d.px)
        .attr('cy', d => d.py)
      d3.selectAll('.stateview-hull')
        .attr('d', d => `M ${d.pnodes.join('L')}Z`)
    }
    else {  // two dimension
      d3.selectAll('.stateview-link')
        .attr('d', d => `M${d.src.x},${d.src.y}
                         L${d.dst.x},${d.dst.y}`)
      d3.selectAll('.stateview-node')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
      d3.selectAll('.stateview-hull')
        .attr('d', d => `M ${d.nodes.join('L')}Z`)
    }
  }
  switchShowGroups(opt) {
    opt ? (d3.selectAll('.stateview-hull').style('opacity', 0.9)) : (d3.selectAll('.stateview-hull').style('opacity', 0))
  }
}
