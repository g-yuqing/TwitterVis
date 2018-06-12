import * as d3 from 'd3'
import Wordcloud from 'Wordcloud'


export default class Splatting {
  constructor() {
    this.width = window.innerWidth*0.6
    this.height = window.innerHeight
    this.yearLabel = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']
  }
  initScene(contourData, wordData) {
    const graph = []
    let xArray = [],
      yArray = []
    for(const key in contourData) {
      const temp = contourData[key]
      if(key!='-1'){
        temp.cluster = key
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
      // })
    function mouseClick(d) {
      const canvas = document.getElementById('word_canvas')
      // const ctx = canvas.getContext('2d')
      // ctx.clearRect(0, 0, canvas.width, canvas.height)
      Wordcloud.minFontSize = '35px'
      Wordcloud(canvas, {
        list: wordData[d.cluster]
      })
    }
  }
}
