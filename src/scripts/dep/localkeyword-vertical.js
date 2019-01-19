import * as d3 from 'd3'
import axios from 'axios'
import {Spinner} from 'spin.js'
import Topiclayout from './topiclayout'

export default class LocalKeyword {
  constructor() {
  }
  initScene(keywordData, newsData, dateHull) {
    // keywordData: [{date: '', kwscore: [['kw', 'score'], ['kw', 'score']]}]
    // dateHull: {date: {group, state}}
    document.getElementById('local-keyword').innerHTML = ''
    const tl = new Topiclayout(),
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
    const datelist = keywordData.map(d => d.date)
    const nodes = []
    let links = []
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
          score = kwscore[1],
          ranking = i
        dateScore[date].push(score)
        if(kw in topWordCoords) {
          topWordCoords[kw].push([date, score, ranking])
        }
        else {
          topWordCoords[kw] = [[date, score, ranking]]
        }
      }
    })
    // render
    // ----------------------- lines -----------------------
    const margin = {top: 30, right: 10, bottom: 10, left:20},
      rowHeight = 80,
      height = datelist.length*rowHeight,
      width = document.getElementById('local-keyword').offsetWidth-margin.left-margin.right,
      lineWidth = width * 0.4,
      titleWidth = width * 0.1,
      newsWidth = width * 0.5
    const svg = d3.select(document.getElementById('local-keyword')).append('svg')
      .attr('id', 'local-keyword-svg')
      .attr('width', width+margin.left+margin.right)
      .attr('height', height+margin.top+margin.bottom)
    const g = svg.append('g')
      .attr('id', 'local-keyword-line-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
      .attr('width', lineWidth)
      .attr('height', height)
    // draw tooltip
    const tooltip = d3.select('body').append('div')
      .attr('id', 'local-keyword-tooltip')
      .attr('class', 'local-keyword-tooltip')
      .style('visibility', 'hidden')
    // x, y axis
    const yScale = d3.scaleBand()
      .domain(datelist)
      .range([0, height])
      .paddingInner(0.03)
    const xScales = {}
    for(const date of datelist) {
      const xScale = d3.scaleLinear()
        .domain(d3.extent(dateScore[date]))
        .range([lineWidth, 0])
      xScales[date] = xScale
    }
    for(const [word, coords] of Object.entries(topWordCoords)) {  // coords: [date, score]
      let color = '#FECEAB',  // leap color
        tempLinks = []
      const wordlinks = []
      const worddates = coords.map(d => d[0])
      for(const date of datelist) {
        const i = worddates.indexOf(date)
        const xScale = xScales[date]
        if(i != -1) {
          // set nodes & links
          const  coord = coords[i],
            x = xScale(coord[1]),  // score
            y = yScale(coord[0]),  // date
            ranking = coord[2]
          nodes.push({x: x, y: y, word: word, color: color, ranking: ranking})
          color = '#99B898'
          tempLinks.push({x:x, y:y, word: word})
        }
        else {
          // reset params
          color = '#FECEAB'
          if(tempLinks.length > 1) {
            wordlinks.push(tempLinks)
          }
          tempLinks = []
        }
      }
      if(tempLinks.length > 1) {
        wordlinks.push(tempLinks)
      }
      links = links.concat(wordlinks)
    }
    // draw links
    const line = d3.line()
      .x(d => d.x)
      .y(d => d.y)
      .curve(d3.curveLinear)
      // .curve(d3.curveStepBefore)
    for(const link of links) {
      g.append('g').append('path')
        .datum(link)
        .attr('class', 'local-keyword-link')
        .attr('stroke-width', '1px')
        .attr('stroke', '#A8A7A7')
        .attr('fill', 'none')
        .attr('d', line)
    }
    // draw nodes
    const rectWidth = 3,
      rectHeight = 10
    g.append('g').selectAll('.dot').data(nodes)
      .enter().append('rect')
      .attr('class', 'local-keyword-node')
      .attr('width', rectWidth)
      .attr('height', rectHeight)
      .attr('x', d => d.x-rectWidth/2)
      .attr('y', d => d.y-rectHeight/2)
      .attr('fill', d => d.color)
      .on('mouseover', d => {
        d3.selectAll('.local-keyword-node').each(function(dd) {
          if(dd.word != d.word) {
            d3.select(this).style('opacity', 0.1)
          }
        })
        d3.selectAll('.local-keyword-link').each(function(dd) {
          const wordlist = dd.map(ddd => ddd.word)
          if(!(wordlist.includes(d.word))) {
            d3.select(this).style('stroke-opacity', 0.1)
          }
        })
      })
      .on('mouseout', () => {
        d3.selectAll('.local-keyword-node').style('opacity', null)
        d3.selectAll('.local-keyword-link').style('stroke-opacity', null)
        tooltip.style('visibility', 'hidden')
      })
      .on('mousemove', function(d) {
        tooltip
          .style('left', `${d3.event.pageX}px`)
          .style('top', `${d3.event.pageY}px`)
          .text(`${d.word} / ranking: ${+d.ranking+1}`)
          .style('visibility', 'visible')
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
            console.log(topicGraph)
            console.log('retreive topic graph data successfully')
            tl.initScene(topicGraph, topicSentences)
            spinner.stop()
          })
      })
    // ----------------------- title -----------------------
    const titleG = svg.append('g')
      .attr('id', 'local-keyword-title-g')
      .attr('transform', `translate(${margin.left+lineWidth}, ${margin.top})`)
      .attr('width', titleWidth)
      .attr('height', height)
    let prevGroup = 0,
      prevColor = '#A8A7A7',
      diffColor = '#363636',
      bandwidth = yScale.bandwidth()
    const titleData = datelist.map(d => {
      const curGroup = dateHull[d].group
      let curColor = diffColor
      if(prevGroup==curGroup) {
        curColor = prevColor
      }
      else {
        prevGroup = curGroup
        diffColor = prevColor
        prevColor = curColor
      }
      return {
        x: titleWidth/2,
        y: yScale(d),
        date: d,
        color: curColor,
        bandwidth: bandwidth
      }
    })
    titleG.append('g').selectAll('.title').data(titleData)
      .enter().append('text')
      .attr('class', 'local-keyword-text')
      .text(d => d.date)
      .attr('x', d => d.x)
      .attr('y', d => d.y+1)
      .attr('fill', d => d.color)
      .style('font-weight', 'bold')
      .style('text-anchor', 'middle')
      .style('font-size', '10px')
    // draw background
    const background = titleG.append('g')
      .attr('transform', `translate(${titleWidth-3}, ${-yScale.bandwidth()/2})`)
    const hullColor = ['#99B898', '#FECEAB', '#FF847C', '#E84A5F']
    background.selectAll('.background').data(titleData)
      .enter().append('rect')
      .attr('class', 'local-keyword-background')
      .attr('y', d => yScale(d.date))
      .attr('width', 3)
      .attr('height', d => d.bandwidth)
      .attr('fill', d => hullColor[dateHull[d.date].state])
      .attr('fill-opacity', 1)
    // ----------------------- news -----------------------
    const newsG = svg.append('g')
      .attr('id', 'local-keyword-title-g')
      .attr('transform', `translate(${margin.left+lineWidth+titleWidth}, ${margin.top})`)
      .attr('width', newsWidth)
      .attr('height', height)

  }
  switchShowGroups(opt) {
    opt ?
      (d3.selectAll('.local-keyword-background').style('fill-opacity', 0.9)) :
      (d3.selectAll('.local-keyword-background').style('fill-opacity', 0))
  }
}
