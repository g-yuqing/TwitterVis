import * as d3 from 'd3'


export default class Mdslayout {
  constructor() {
    this.colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
      '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',
      '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000',
      '#ffd8b1', '#000080', '#808080', '#FFFFFF', '#000000']
    this.years = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
  }
  initScene(dataset, tags) {
    const margin = {top: 30, right: 50, bottom: 10, left:20},
      width = 150,
      height = 900,
      cellHeight = 100,
      cellSpace = 10
    const svg = d3.select(document.getElementById('mdslayout')).append('svg')
      .attr('id', 'mds-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const dataArray = this.years.map(d => dataset[d])
    for(const i in dataArray) {
      const data = dataArray[i]
      const xScale = d3.scaleLinear()
        .range([0, width])
        .domain(d3.extent(data, d => d.x))
      const yScale = d3.scaleLinear()
        .range([cellHeight, 0])
        .domain(d3.extent(data, d => d.y))
      const g = svg.append('g')
        .attr('id', `mds-g${i}`)
        .attr('transform', `translate(${margin.left}, ${margin.top})`)
      g.selectAll('.dot').data(data)
        .enter().append('circle')
        .attr('class', 'dot')
        .attr('r', 2.5)
        .attr('cx', d => xScale(d.x))
        .attr('cy', d => yScale(d.y)+i*(cellHeight+cellSpace))
        .style('fill', d => {
          for(const t in tags) {
            const tag = tags[t]
            if(d.noun.includes(tag)) {
              return this.colors[i]
            }
          }
          return '#80808033'
        })
        .on('click', d => {
          console.log(d.text)
          this.eventHub.$emit('initTextlayoutScene')
        })
    }
  }
  updateScene(tags) {
    for(const i in this.years) {
      d3.select(`#mds-g${i}`).selectAll('circle')
        .style('fill', d => {
          for(const t in tags) {
            const tag = tags[t]
            if(d.noun.includes(tag)) {
              return this.colors[i]
            }
          }
          return '#80808033'
        })
    }
  }
}
