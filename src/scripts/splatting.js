import * as d3 from 'd3'


export default class Splatting {
  constructor() {
    this.width = window.innerWidth*0.4
    this.height = window.innerHeight*0.3
    this.yearLabel = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
  }
  initScene(year) {
    fetch('../static/clustered/cluster_counter.json').then(res => res.json())
      .then(dataset => {
        const data = dataset[this.yearLabel[year]]
        const graph = []
        let xArray = [],
          yArray = []
        for(const key in data) {
          const temp = data[key]
          if(key!='-1'){
            graph.push(temp)
          }
          const boundaryX = temp.boundary.map(d => d.x)
          const boundaryY = temp.boundary.map(d => d.y)
          xArray = xArray.concat(boundaryX)
          yArray = yArray.concat(boundaryY)
        }
        const size = Math.min(this.width, this.height)
        const xScale = d3.scaleLinear()
          .domain(d3.extent(xArray))
          .range([0, size])
        const yScale = d3.scaleLinear()
          .domain(d3.extent(yArray))
          .range([size, 0])
        document.getElementById('splatting').innerHTML = ''
        const svg = d3.select(document.getElementById('splatting')).append('svg')
          .attr('width', this.width)
          .attr('height', this.height)
        svg.selectAll('polygon')
          .data(graph)
          .enter().append('polygon')
          .attr('points', d => {
            return d.boundary.map(dd => {
              return [xScale(dd.x), yScale(dd.y)].join(',')
            }).join(',')
          })
          .attr('stroke', d => d.color)
          .attr('fill', d => `${d.color}26`)
          .on('click', d => mouseClick(d))
      })
    function mouseClick(d) {
      console.log(d.color)
    }
  }
}
