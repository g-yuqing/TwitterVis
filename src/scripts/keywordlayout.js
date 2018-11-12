import * as d3 from 'd3'


export default class Keywordlayout {
  constructor() {

  }
  initScene() {
    // required parameters
    const dates = [],
      dateKw = {},
      selectedKw = [],
      dateText = {}
    const margin = {top: 70, right: 50, bottom: 10, left:20},
      width = 960,
      height = 300
    const svg = d3.select(document.getElementById('keywordview')).append('svg')
      .attr('id', 'keyword-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const g = svg.append('g')
      .attr('id', 'keyword-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
    const xScale = d3.scaleLinear()
      .range([0, width])
      .domain([0, dates.lengths])
    const currentKeywords = []
    for(const i in dates) {
      const curDate = dates[i]
      const textArray = dateText[curDate]
      for(const j in textArray) {
        const curText = textArray[j]
      }
    }
  }
}
