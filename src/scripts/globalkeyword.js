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
    const margin = {top: 40, bottom: 5, left: 50, right: 20},
      padding = {bottom: 10, right: 30},
      keywords = sortKwScore.map(d => d[0]),
      height = 220 - margin.top - margin.bottom,
      colHeight = 25,
      cellHeight = colHeight + padding.bottom,
      colWidth = 60,
      cellWidth = colWidth + padding.right,
      countPerCol = Math.floor(height/cellHeight),  // the number of line in each column
      colCount = Math.floor(keywords.length/countPerCol)+1,  // the number of column
      // width = window.innerWidth*0.6-margin.left-margin.right,
      width = colCount * cellWidth
      // cellWidth = width / colCount,
      // colWidth = cellWidth - padding.right
    const svg = d3.select(document.getElementById('global-keyword')).append('svg')
      .attr('id', 'global-keyword-svg')
      // .attr('width', width+margin.left)
      .attr('width', width+margin.left+margin.right)
      .attr('height', height+margin.top+margin.bottom)
    const g = svg.append('g')
      .attr('id', 'global-keyword-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
      .attr('width', width)
      .attr('height', height)
    const colorScale = d3.scaleLinear()
      .domain([sortKwScore[0][1], sortKwScore[sortKwScore.length-1][1]])
      .range(['#E84A5F', '#99B898'])
      .interpolate(d3.interpolateLab)
    const xScale = d3.scalePoint()
      .domain(datelist)
      .range([0, colWidth])
    // draw lines
    for(const i in keywords) {
      const kw = keywords[i],
        data = nodes[kw],
        score = kwScore[kw],  // socre in total
        color = colorScale(score)
      const yScale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.score))
        .range([colHeight, 0])
      const line = d3.line()
        .x(d => xScale(d.date))
        .y(d => yScale(d.score))
        .curve(d3.curveMonotoneX)
      // const cellG = g.append('g')
      //   .attr('transform', `translate(0, ${i*cellHeight})`)
      //   .attr('class', 'global-keyword-text')
      const offsetX = Math.floor(i/countPerCol)*cellWidth,
        offsetY = i%countPerCol*cellHeight
      const cellG = g.append('g')
        .attr('transform', `translate(${offsetX}, ${offsetY})`)
        .attr('class', 'global-keyword-text')
        .attr('id', `global-keyword-g-${kw}`)
      cellG.append('text')
        .attr('class', 'global-keyword-text')
        .text(kw)
        .attr('x', 0)
        .attr('y', yScale(data[0].score))
        .attr('text-anchor', 'end')
        .attr('fill', color)
      cellG.append('path')
        .datum(data)
        .attr('class', 'global-keyword-link')
        .attr('id', `global-keyword-link-${kw}`)
        .attr('stroke-width', '1px')
        .attr('stroke', color)
        .attr('fill', 'none')
        .attr('d', line)
    }
    // // mouse line
    // const mouseG = g.append('g')
    //   .attr('class', 'global-keyword-mouse-g')
    //   // .attr('transform', `translate(0, 0)`)
    // mouseG.append('rect')
    //   .attr('width', width)
    //   .attr('height', height)
    //   .attr('fill', 'none')
    //   .attr('pointer-events', 'all')
    //   .on('mouseout', function() {
    //     d3.select('.global-keyword-mouseline')
    //       .style('opacity', 0)
    //     d3.select('#global-keyword-mousetag')
    //       .style('opacity', 0)
    //   })
    //   .on('mouseover', function() {
    //     d3.select('.global-keyword-mouseline')
    //       .style('opacity', 1)
    //     d3.select('#global-keyword-mousetag')
    //       .style('opacity', 1)
    //   })
    //   .on('mousemove', function() {
    //     const x0 = d3.mouse(this)[0]
    //     // invert of x0
    //     const domain = xScale.domain(),
    //       range = xScale.range(),
    //       rangePoints = d3.range(range[0], range[1], xScale.step()),
    //       x1 = domain[d3.bisect(rangePoints, x0) -1]
    //     d3.select('#global-keyword-mousetag')
    //       .text(x1)
    //       .attr('y', d3.mouse(this)[1])
    //     d3.select('.global-keyword-mouseline')
    //       .attr('d', `M${x0} ${height}L${x0} 0`)
    //   })
    // mouseG.append('path')
    //   .attr('class', 'global-keyword-mouseline')
    //   .attr('stroke', '#2A363B')
    //   .attr('stroke-width', '1px')
    //   .style('opacity', '0')
    // mouseG.append('text')
    //   .attr('class', 'keyword-text')
    //   .attr('id', 'global-keyword-mousetag')
    //   .attr('x', 0)
    //   .attr('dy', '.31em')
    //   .attr('text-anchor', 'end')
    //   .style('font-size', '10px')
    //   .style('opacity', 0)
  }
}
