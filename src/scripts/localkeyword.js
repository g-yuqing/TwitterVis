import * as d3 from 'd3'
import axios from 'axios'
import {Spinner} from 'spin.js'
import Topiclayout from './topiclayout'

export default class LocalKeyword {
  constructor() {
  }
  // initScene(keywordData, newsData, dateHull) {
  initScene(stateData, keywordDataAll, newsData) {
    // keywordData: [{date: '', kwscore: [['kw', 'score'], ['kw', 'score']]}]
    // dateHull: {date: {group, state}}
    let minProp = 1,
      maxProp = 0
    const keywordData = [],
      dateHull = {}
    for(const node of stateData.nodes) {
      let allScore = 0
      for(const kwScore of keywordDataAll.period[node.date]) {
        allScore += kwScore[1]
      }
      const kwProp = keywordDataAll.period[node.date].map(d => {
        const kw = d[0],
          prop = d[1]/allScore
        if(prop>maxProp) {maxProp = prop}
        if(prop<minProp) {minProp = prop}
        return [kw, prop]
      })
      keywordData.push({
        date: node.date,
        kwscore: kwProp
      })
      dateHull[node.date] = {
        group: node.g,
        state: node.state
      }
    }
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
      topCount = 20,
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
    const margin = {top: 60, right: 10, bottom: 10, left:50},
      colWidth = 60,
      width = datelist.length*colWidth,
      height = document.getElementById('local-keyword').offsetHeight-margin.top-margin.bottom
    const svg = d3.select(document.getElementById('local-keyword')).append('svg')
      .attr('id', 'local-keyword-svg')
      .attr('width', width+margin.left+margin.right)
      .attr('height', height+margin.top+margin.bottom)
    const g = svg.append('g')
      .attr('id', 'local-keyword-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
      .attr('width', width)
      .attr('height', height)
    // draw tooltip
    const tooltip = d3.select('body').append('div')
      .attr('id', 'local-keyword-tooltip')
      .attr('class', 'local-keyword-tooltip')
      .style('visibility', 'hidden')
    // x, y axis
    const xScale = d3.scaleBand()
      .domain(datelist)
      .range([0, width])
      .paddingInner(0.03)
    const yScales = {}
    for(const date of datelist) {
      const yScale = d3.scaleLinear()
        .domain(d3.extent(dateScore[date]))
        .range([height, 0])
      yScales[date] = yScale
    }
    // const yScale = d3.scaleLinear()
    //   .domain([minProp, maxProp])
    //   .range([height, 0])
    for(const [word, coords] of Object.entries(topWordCoords)) {  // coords: [date, idx]
      let color = '#FECEAB',  // leap color
        tempLinks = []
      const wordlinks = []
      const worddates = coords.map(d => d[0])
      for(const date of datelist) {
        const i = worddates.indexOf(date)
        const yScale = yScales[date]
        if(i != -1) {
          // set nodes & links
          const  coord = coords[i],
            x = xScale(coord[0]),
            y = yScale(coord[1]),
            ranking = coord[2]
          nodes.push({x: x, y: y, word: word, color: color, ranking: ranking, date: date})
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
    const rectWidth = 10,
      rectHeight = 6,
      newsDiv = d3.select(document.getElementById('newsview')).append('div')
        .attr('id', 'newsview-div')
        .attr('class', 'newsview')
    g.append('g').selectAll('.dot').data(nodes)
      .enter().append('rect')
      .attr('class', 'local-keyword-node')
      // .text(d => d.word)
      // .attr('x', d => d.x)
      // .attr('y', d => d.y)
      .attr('width', rectWidth)
      .attr('height', rectHeight)
      .attr('x', d => d.x-rectWidth/2)
      .attr('y', d => d.y-rectHeight/2)
      .attr('fill', d => d.color)
      // .style('text-anchor', 'middle')
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
        // trigger news loading
        document.getElementById('newsview-div').innerHTML = ''
        let newsList = []
        let htmlContent = `<div class='title'>News</div><div class='title'>${d.date}</div><div class='content'>keyword: ${d.word} ranking: ${+d.ranking+1}</div>`
        const idx = datelist.indexOf(d.date)  // 3 days early, 5 days latter
        const early = idx>=3?idx-3:0,
          latter = 5
        for(let ii=0;ii<early;ii++) {  // early
          const news = newsData[datelist[idx+ii]]
          if(news !== undefined) {
            newsList = newsList.concat(news)
          }
        }
        for(let ii=0;ii<latter;ii++) {  // latter
          const news = newsData[datelist[idx+ii]]
          if(news !== undefined) {
            newsList = newsList.concat(news)
          }
        }
        for(const news of newsList) {
          const title = news.title,
            content = news.content
          if(title.includes(d.word)) {
            htmlContent += `<div class='title'>${title}</div>`
            htmlContent += `<div class='content'>${content}</div>`
          }
        }
        newsDiv.html(htmlContent)
        // trigger tweet loading
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
    // test2-----------------------------------------------
    const testDate = ['2019-01-07', '2019-01-20', '2019-02-01', '2019-02-10'],
      testColor = ['#594F4F', '#547980', '#45ADA8', '#9DE0AD'],
      testDate1 = ['2019-01-08', '2019-01-21', '2019-02-02', '2019-02-11'],
      testDate2 = ['2019-01-09', '2019-01-22', '2019-02-03', '2019-02-12'],
      testDate3 = ['2019-01-10', '2019-01-23', '2019-02-04', '2019-02-13']
    const colorScale = d3.scaleSequential(d3.interpolateYlOrRd)
      .domain([0, datelist.length])
    const titleG = svg.append('g')
      .attr('id', 'local-keyword-title-g')
      .attr('transform', `translate(${margin.left}, ${margin.top/3})`)
      .attr('width', width)
      .attr('height', margin.top)
    const titleData = datelist.map((d, i) => {
      let color = testDate.indexOf(d) != -1 ? testColor[testDate.indexOf(d)] : colorScale(i)
      //test3-----------------------------------------------
      if(testDate1.indexOf(d)!=-1) {
        color = testColor[testDate1.indexOf(d)]
      }
      if(testDate2.indexOf(d)!=-1) {
        color = testColor[testDate2.indexOf(d)]
      }
      if(testDate3.indexOf(d)!=-1) {
        color = testColor[testDate3.indexOf(d)]
      }
      return {
        x: xScale(d),
        y: 0,
        date: d,
        color: color
      }
    })
    titleG.append('g').selectAll('.title').data(titleData)
      .enter().append('text')
      .attr('class', 'local-keyword-title-text')
      .attr('id', d => `local-keyword-title-text-${d.date}`)
      .text(d => d.date)
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('fill', d => d.color)
      .style('text-anchor', 'middle')
      .style('font-size', '10px')
      .style('font-weight', 'bold')
    // draw background
    let bgPrevGroup = dateHull[datelist[0]].group,
      bgTempData = []
    const backgroundDateset = []
    datelist.forEach(d => {
      const bgCurGroup = dateHull[d].group
      if(bgPrevGroup == bgCurGroup) {
        bgTempData.push(d)
      }
      else {
        backgroundDateset.push(bgTempData)
        bgTempData = [d]
      }
      bgPrevGroup = bgCurGroup
    })
    backgroundDateset.push(bgTempData)
    const backgroundData = backgroundDateset.map(d => {
      return {
        x: xScale(d[0])+xScale.bandwidth()*0.3,
        width: xScale(d[d.length-1]) - xScale(d[0]) + xScale.bandwidth() - xScale.bandwidth()*0.3*2,
        height: 3,
        color: '#4682b4'
      }
    })
    const background = titleG.append('g')
      .attr('transform', `translate(${-xScale.bandwidth()/2}, 3)`)
    // const hullColor = ['#99B898', '#FECEAB', '#FF847C', '#E84A5F']
    background.selectAll('.background').data(backgroundData)
      .enter().append('rect')
      .attr('class', 'local-keyword-background')
      .attr('x', d => d.x)
      .attr('width', d => d.width)
      .attr('height', d => d.height)
      .attr('fill', d => d.color)
      // .attr('fill', d => hullColor[dateHull[d].state])
      .attr('fill-opacity', 1)

  }
  switchShowGroups(opt) {
    opt ?
      (d3.selectAll('.local-keyword-background').style('fill-opacity', 0.9)) :
      (d3.selectAll('.local-keyword-background').style('fill-opacity', 0))
  }
}
