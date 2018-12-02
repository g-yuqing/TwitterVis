import * as d3 from 'd3'
import axios from 'axios'
import {Spinner} from 'spin.js'
import Topiclayout from './topiclayout'


export default class Keywordlayout {
  constructor() {
  }
  initScene(keywordData, hullDates) {
    // keywordData: [{date: '', kwscore: [['kw', 'score'], ['kw', 'score']]}]
    // hullDates: {group: [date1, date2]}
    const datelist = keywordData.map(d => d.date),
      tl = new Topiclayout(),
      loadOpt = {
        lines: 9, // The number of lines to draw
        length: 9, // The length of each line
        width: 5, // The line thickness
        radius: 14, // The radius of the inner circle
        color: '#FF847C', // #rgb or #rrggbb or array of colors
        speed: 1, // Rounds per second
        trail: 40, // Afterglow percentage
        className: 'spinner', // The CSS class to assign to the spinner
      }
    // empty previous visualization
    document.getElementById('keyword-tendency').innerHTML = ''
    document.getElementById('keyword-overview').innerHTML = ''

    const kwScore = {},  // {keyword: score}
      sortKwScore = [],  // [[word: score], [], []]
      wordCoords = {}  // {word: [[date1, idx1], [date2, idx2]]}
    // init kwScore, wordCoords
    // ============================ init keyword-tendency ============================
    keywordData.forEach(dateKwscore => {  // keywordData: [{date: '', kwscore: [['kw', 'score'], ['kw', 'score']]}]
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
    // prepare nodes and links data
    const tdyNodes = {}  // {word: [{date, score}, {date, score}]}
    for(const [word, coordsList] of Object.entries(wordCoords)) {
      // init coordsDict
      let coordsDict = {}
      tdyNodes[word] = []
      datelist.forEach(d => {
        coordsDict[d] = 0
      })
      for(const coord of coordsList) {
        const date = coord[0],
          score = coord[1]
        coordsDict[date] = score
      }
      for(const [date, score] of Object.entries(coordsDict)) {
        tdyNodes[word].push({date: date, score: score})
      }
    }
    // render
    const tdyWidth = 250,
      tdyTopPadding = 20,
      tdyLeftPadding = 80,
      tdyBottomPadding = 10,
      tdySubHeight = 50,
      tdyCellHeight = tdyBottomPadding+tdySubHeight,
      tdyHeight = sortKwScore.length * (tdyBottomPadding+tdySubHeight),
      keywords = sortKwScore.map(d => d[0])
    const tdySvg = d3.select(document.getElementById('keyword-tendency')).append('svg')
      .attr('id', 'keyword-tendency-svg')
      .attr('width', tdyWidth)
      .attr('height', tdyHeight)
    const tdyG = tdySvg.append('g')
      .attr('id', 'keyword-tendency-g')
      .attr('transform', `translate(0, ${tdyTopPadding})`)
      .attr('width', tdyWidth)
      .attr('height', tdyHeight)
    const tdyColorScale = d3.scaleLinear()
      .domain([sortKwScore[0][1], sortKwScore[sortKwScore.length-1][1]])
      .range(['#E84A5F', '#99B898'])
      .interpolate(d3.interpolateLab)
    const tdyXScale = d3.scalePoint()
      .domain(datelist)
      .range([tdyLeftPadding, tdyWidth])
    // draw line
    for(const i in keywords) {
      const kw = keywords[i]
      const data = tdyNodes[kw]
      const score = kwScore[kw],
        color = tdyColorScale(score)
      const tdyYScale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.score))
        .range([tdySubHeight, 0])
      const tdyLine = d3.line()
        .x(d => tdyXScale(d.date))
        .y(d => tdyYScale(d.score))
        .curve(d3.curveMonotoneX)
      const tdyCellG = tdyG.append('g')
        .attr('transform', `translate(0, ${i*tdyCellHeight})`)
        .attr('class', 'keyword-text')
      tdyCellG.append('text')
        .attr('class', 'keyword-text')
        .text(kw)
        .attr('x', tdyLeftPadding)
        .attr('y', tdyYScale(data[0].score))
        .attr('text-anchor', 'end')
        .attr('fill', color)
      tdyCellG.append('path')
        .datum(data)
        .attr('class', 'keyword-tendency-link')
        .attr('stroke-width', '1px')
        .attr('stroke', color)
        .attr('fill', 'none')
        .attr('d', tdyLine)
    }
    // mouse line
    const tdyMouseG = tdyG.append('g')
      .attr('class', 'keyword-tendency-mouse-g')
      .attr('transform', `translate(${tdyLeftPadding}, 0)`)
    tdyMouseG.append('rect')
      .attr('width', tdyWidth-tdyLeftPadding)
      .attr('height', tdyHeight)
      .attr('fill', 'none')
      .attr('pointer-events', 'all')
      .on('mouseout', function() {
        d3.select('.keyword-tendency-mouseline')
          .style('opacity', 0)
        d3.select('#keyword-tendency-mousetag')
          .style('opacity', 0)
      })
      .on('mouseover', function() {
        d3.select('.keyword-tendency-mouseline')
          .style('opacity', 1)
        d3.select('#keyword-tendency-mousetag')
          .style('opacity', 1)
      })
      .on('mousemove', function() {
        const x0 = d3.mouse(this)[0]
        // invert of x0
        const domain = tdyXScale.domain(),
          range = tdyXScale.range(),
          rangePoints = d3.range(range[0]-tdyLeftPadding, range[1], tdyXScale.step()),
          x1 = domain[d3.bisect(rangePoints, x0) -1]
        d3.select('#keyword-tendency-mousetag')
          .text(x1)
          .attr('y', d3.mouse(this)[1])
        d3.select('.keyword-tendency-mouseline')
          .attr('d', `M${x0} ${tdyHeight}L${x0} 0`)
      })
    tdyMouseG.append('path')
      .attr('class', 'keyword-tendency-mouseline')
      .attr('stroke', '#2A363B')
      .attr('stroke-width', '1px')
      .style('opacity', '0')
    tdyMouseG.append('text')
      .attr('class', 'keyword-text')
      .attr('id', 'keyword-tendency-mousetag')
      .attr('x', 0)
      .attr('dy', '.31em')
      .attr('text-anchor', 'end')
      .style('font-size', '10px')
      .style('opacity', 0)
    // ============================ init keyword-overview ============================
    // changed word : #99B898 else: #FECEAB
    // leap date: #E84A5F else: #2A3633B
    const overMargin = {top: 60, right: 10, bottom: 50, left:50},
      overColWidth = 60,
      overWidth = datelist.length * overColWidth,
      overHeight = document.getElementById('keyword-overview').offsetHeight-overMargin.top-overMargin.bottom
    const overSvg = d3.select(document.getElementById('keyword-overview')).append('svg')
      .attr('id', 'keyword-overview-svg')
      .attr('width', overWidth+overMargin.left+overMargin.right)
      .attr('height', overHeight+overMargin.top+overMargin.bottom)
    const overG = overSvg.append('g')
      .attr('id', 'keyword-overview-g')
      .attr('transform', `translate(${overMargin.left}, ${overMargin.top})`)
      .attr('width', overWidth)
      .attr('height', overHeight)
    // prepare data
    const overNodes = []
    let overLinks = []
    const topWordCoords = {},
      topCount = 10,
      dateScore = {}
    keywordData.forEach(dateKwscore => {  // keywordData: [{date: '', kwscore: [['kw', 'score'], ['kw', 'score']]}]
      const date = dateKwscore.date,
        kwscoreList = dateKwscore.kwscore.slice(0, topCount)
      dateScore[date] = []
      for(const i in kwscoreList) {
        const kwscore = kwscoreList[i],
          kw = kwscore[0],
          score = kwscore[1]
        dateScore[date].push(score)
        if(kw in topWordCoords) {
          topWordCoords[kw].push([date, score])
        }
        else {
          topWordCoords[kw] = [[date, score]]
        }
      }
    })
    // const overXScale = d3.scalePoint()
    const overXScale = d3.scaleBand()
      .domain(datelist)
      .range([0, overWidth])
      .paddingInner(0.0)
    const overYScales = {}
    for(const date of datelist) {
      const overYScale = d3.scaleLinear()
        .domain(d3.extent(dateScore[date]))
        .range([overHeight, 0])
      overYScales[date] = overYScale
    }
    for(const [word, coords] of Object.entries(topWordCoords)) {  // coords: [date, idx]
      let color = '#E84A5F',  // leap color
        tempLinks = []
      const wordlinks = []
      const worddates = coords.map(d => d[0])
      for(const date of datelist) {
        const i = worddates.indexOf(date)
        const overYScale = overYScales[date]
        if(i != -1) {
          // set nodes & links
          const  coord = coords[i],
            x = overXScale(coord[0]),
            y = overYScale(coord[1])
          overNodes.push({x: x, y: y, word: word, color: color})
          color = '#2A3633B'
          tempLinks.push({x:x, y:y, word: word})
        }
        else {
          // reset params
          color = '#E84A5F'
          if(tempLinks.length > 1) {
            wordlinks.push(tempLinks)
          }
          tempLinks = []
        }
      }
      if(tempLinks.length > 1) {
        wordlinks.push(tempLinks)
      }
      overLinks = overLinks.concat(wordlinks)
    }
    // render
    // draw title
    const overTitleG = overSvg.append('g')
      .attr('id', 'keyword-overview-title-g')
      .attr('transform', `translate(${overMargin.left}, ${overMargin.top/3})`)
      .attr('width', overWidth)
      .attr('height', overMargin.top)
    const titleData = datelist.map((d, i) => {
      return {
        x: overXScale(d),
        y: 0,
        text: d,
        color: (i%2==0?'#2A3633B':'#474747')
      }
    })
    overTitleG.append('g').selectAll ('.title').data(titleData)
      .enter().append('text')
      .attr('class', 'keyword-text')
      .text(d => d.text)
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('fill', d => d.color)
      .style('text-anchor', 'middle')
      .style('font-size', '10px')
    // draw background
    const overBackground = overG.append('g')
      .attr('transform', `translate(${-overXScale.bandwidth()/2}, -12)`)
    const dateColor = {}
    const hullColor = ['#99B898', '#FECEAB', '#FF847C', '#E84A5F']
    for(const [group, datelist] of Object.entries(hullDates)) {
      for(const date of datelist) {
        dateColor[date] = hullColor[(+group)%4]
      }
    }
    overBackground.selectAll('.background').data(datelist)
      .enter().append('rect')
      .attr('class', 'keyword-background')
      .attr('x', d => overXScale(d))
      .attr('width', overXScale.bandwidth())
      .attr('height', overHeight+15)
      .attr('fill', d => dateColor[d])
      .attr('fill-opacity', 0)
    // draw link
    const overLine = d3.line()
      .x(d => d.x)
      .y(d => d.y)
      .curve(d3.curveMonotoneX)
    for(const link of overLinks) {
      overG.append('g').append('path')
        .datum(link)
        .attr('class', 'keyword-overview-link')
        .attr('stroke-width', '1px')
        .attr('stroke', '#A8A7A7')
        .attr('fill', 'none')
        .attr('d', overLine)
    }
    // draw nodes
    overG.append('g').selectAll('.dot').data(overNodes)
      .enter().append('text')
      .attr('class', 'keyword-text')
      .text(d => d.word)
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('fill', d => d.color)
      .style('text-anchor', 'middle')
      .on('mouseover', d => {
        d3.selectAll('.keyword-overview-node').each(function(dd) {
          if(dd.word != d.word) {
            d3.select(this).style('opacity', 0.1)
          }
        })
        d3.selectAll('.keyword-overview-link').each(function(dd) {
          const wordlist = dd.map(ddd => ddd.word)
          if(!(wordlist.includes(d.word))) {
            d3.select(this).style('stroke-opacity', 0.1)
          }
        })
      })
      .on('mouseout', () => {
        d3.selectAll('.keyword-overview-node').style('opacity', null)
        d3.selectAll('.keyword-overview-link').style('stroke-opacity', null)
      })
      .on('click', d => {
        // trigger loading
        const spinner = new Spinner(loadOpt).spin(document.getElementById('topicview'))
        const params = new URLSearchParams()
        params.set('keyword', d.word)
        for(const date of datelist) {
          params.append('dates', date)
        }
        const url = `http://127.0.0.1:5000/topic/${params.toString()}`
        axios.get(url, { crossdomain: true })
          .then(res => {
            const topicGraph = res.data[0],
              topicSentences = res.data[1]
            console.log('retreive topic graph data successfully')
            tl.initScene(topicGraph, topicSentences)
            spinner.stop()
          })
      })
  }
  switchShowGroups(opt) {
    opt ? (d3.selectAll('.keyword-background').style('fill-opacity', 0.3)) : (d3.selectAll('.keyword-background').style('fill-opacity', 0))
  }
}
