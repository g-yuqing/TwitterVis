import * as d3 from 'd3'


export default class GlobalKeyword {
  constructor() {
  }
  initScene(stateData, keywordData) {
    document.getElementById('global-keyword').innerHTML = ''
    const dateKwsList = []
    stateData.nodes.forEach(d => {
      dateKwsList.push({
        date: d.date,
        kwscore: keywordData.period[d.date]
      })
    })
    const kwScore = {},  // {keyword: score}
      sortKwScore = [],  // [[word: score], [], []]
      wordCoords = {},  // {word: [[date1, idx1], [date2, idx2]]}
      datelist = dateKwsList.map(d => d.date)
    dateKwsList.forEach(dateKwscore => {
      const date = dateKwscore.date,
        kwscoreList = dateKwscore.kwscore
      for(const i in kwscoreList) {
        const kwscore = kwscoreList[i],
          kw = kwscore[0],
          score = kwscore[1]
        if(kw in kwScore) {
          kwScore[kw] += score
          wordCoords[kw].push([date, score])
        }
        else {
          kwScore[kw] = score
          wordCoords[kw] = [[date, score]]
        }
      }
    })
    // sort kwScore
    for(const [word, score] of Object.entries(kwScore)) {
      sortKwScore.push([word, score])
    }
    sortKwScore.sort((a, b) => (b[1] - a[1]))
    // init nodes
    const nodes = {}  // {word: [{date, score}, {date, score}]}
    for(const [word, coordsList] of Object.entries(wordCoords)) {
      let coordsDict = {}
      nodes[word] = []
      datelist.forEach(d => {coordsDict[d] = 0})  // initialization
      for(const coord of coordsList) {
        const date = coord[0],
          score = coord[1]
        coordsDict[date] = score
      }
      for(const [date, score] of Object.entries(coordsDict)) {
        nodes[word].push({date: date, score: score})
      }
    }
    // render
    const padding = {top: 20, bottom: 5, left: 50},
      width = 300,
      subHeight = 30,
      cellHeight = subHeight + padding.bottom,
      height = sortKwScore.length*(padding.bottom+subHeight),
      keywords = sortKwScore.map(d => d[0])
    const svg = d3.select(document.getElementById('global-keyword')).append('svg')
      .attr('id', 'global-keyword-svg')
      .attr('width', width+padding.left)
      .attr('height', height+padding.top+padding.bottom)
    const g = svg.append('g')
      .attr('id', 'global-keyword-g')
      .attr('transform', `translate(0, ${padding.top})`)
      .attr('width', width)
      .attr('height', height)
    const colorScale = d3.scaleLinear()
      .domain([sortKwScore[0][1], sortKwScore[sortKwScore.length-1][1]])
      .range(['#E84A5F', '#99B898'])
      .interpolate(d3.interpolateLab)
    const xScale = d3.scalePoint()
      .domain(datelist)
      .range([padding.left, width])
    // draw lines
    for(const i in keywords) {
      const kw = keywords[i],
        data = nodes[kw],
        score = kwScore[kw],
        color = colorScale(score)
      const yScale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.score))
        .range([subHeight, 0])
      const line = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScale(d.score))
        .curve(d3.curveMonotoneX)
      const cellG = g.append('g')
        .attr('transform', `translate(0, ${i*cellHeight})`)
        .attr('class', 'global-keyword-text')
      cellG.append('text')
        .attr('class', 'global-keyword-text')
        .text(kw)
        .attr('x', padding.left)
        .attr('y', yScale(data[0].score))
        .attr('text-anchor', 'end')
        .attr('fill', color)
      cellG.append('path')
        .datum(data)
        .attr('class', 'global-keyword-link')
        .attr('stroke-width', '1px')
        .attr('stroke', color)
        .attr('fill', 'none')
        .attr('d', line)
    }
    // mouse line
    const mouseG = g.append('g')
      .attr('class', 'global-keyword-mouse-g')
      .attr('transform', `translate(${padding.left}, 0)`)
    mouseG.append('rect')
      .attr('width', width-padding.left)
      .attr('height', height)
      .attr('fill', 'none')
      .attr('pointer-events', 'all')
      .on('mouseout', function() {
        d3.select('.global-keyword-mouseline')
          .style('opacity', 0)
        d3.select('#global-keyword-mousetag')
          .style('opacity', 0)
      })
      .on('mouseover', function() {
        d3.select('.global-keyword-mouseline')
          .style('opacity', 1)
        d3.select('#global-keyword-mousetag')
          .style('opacity', 1)
      })
      .on('mousemove', function() {
        const x0 = d3.mouse(this)[0]
        // invert of x0
        const domain = xScale.domain(),
          range = xScale.range(),
          rangePoints = d3.range(range[0]-padding.left, range[1], xScale.step()),
          x1 = domain[d3.bisect(rangePoints, x0) -1]
        d3.select('#global-keyword-mousetag')
          .text(x1)
          .attr('y', d3.mouse(this)[1])
        d3.select('.global-keyword-mouseline')
          .attr('d', `M${x0} ${height}L${x0} 0`)
      })
    mouseG.append('path')
      .attr('class', 'global-keyword-mouseline')
      .attr('stroke', '#2A363B')
      .attr('stroke-width', '1px')
      .style('opacity', '0')
    mouseG.append('text')
      .attr('class', 'keyword-text')
      .attr('id', 'global-keyword-mousetag')
      .attr('x', 0)
      .attr('dy', '.31em')
      .attr('text-anchor', 'end')
      .style('font-size', '10px')
      .style('opacity', 0)
  }
}
