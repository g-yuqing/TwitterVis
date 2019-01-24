import * as d3 from 'd3'
import * as rgbToHsl from 'rgb-to-hsl'
import * as allToRgb from 'rgb'


export default class Streamlayout {
  constructor() {
  }
  initScene(stateData, keywordData, newsData) {
    document.getElementById('streamview').innerHTML = ''
    // init data
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
    // ===========================================================
    // stack graph
    const layerNum = sortKwScore.length,
      sampleNum = datelist.length,
      stack = d3.stack().keys(d3.range(layerNum).map(d => `layer${d}`)).offset(d3.stackOffsetWiggle)
    const keywords = sortKwScore.slice(0, layerNum)
    let matrix = d3.range(sampleNum).map(d => { return {x: d} })
    for(const layeri in keywords) {
      const kw = keywords[layeri][0],
        dateScoreList = nodes[kw]
      for(const ii in dateScoreList) {
        const dateScore = dateScoreList[ii]
        matrix[ii][`layer${layeri}`] = dateScore.score
      }
    }
    const layers = stack(matrix)
    // render
    const margin = {top: 20, bottom: 10, left: 10, right: 10},
      width = window.innerWidth*0.6-margin.left-margin.right,
      streamHeight = 220,
      axisHeight = 80,
      height = streamHeight+axisHeight
    const xScale = d3.scaleLinear()
      .domain([0, sampleNum-1])
      .range([0, width])
    const yScale = d3.scaleLinear()
      .range([streamHeight, 0])
      .domain([
        d3.min(layers, function(layer) { return d3.min(layer, d => d[0]) }),
        d3.max(layers, function(layer) { return d3.max(layer, d => d[1]) })
      ])
    const area = d3.area()
      .x(d => xScale(d.data.x))
      .y0(d => yScale(d[0]))
      .y1(d => yScale(d[1]))
    const svg = d3.select(document.getElementById('streamview')).append('svg')
      .attr('id', 'streamview-svg')
      .attr('width', width+margin.right+margin.left)
      .attr('height', height+margin.top+margin.bottom)
    // linear gradient
    const colorScale = d3.scaleSequential(d3.interpolateYlOrRd)
      .domain([0, datelist.length-1])
    for(let i=0; i<layerNum; i++) {
      const linearGradient = svg.append('defs')
        .append('linearGradient')
        .attr('id', `linear-gradient${i}`)
      for(const ii in datelist) {
        const rgb = colorScale(ii),  // str
          temp = rgb.substring(4, rgb.length-1).replace(/ /g, '').split(','),  // array
          hsl = rgbToHsl(temp[0], temp[1], temp[2]),  // array
          saturation = +hsl[1].slice(0, hsl[1].length-1),
          offset = saturation / (layerNum*1.5),
          color = allToRgb(`hsl(${hsl[0]}, ${saturation-offset*i}, ${hsl[2]})`)  // str
        linearGradient.append('stop')
          .attr('offset', `${100*ii/datelist.length}%`)
          .attr('stop-color', color)
      }
    }
    const g = svg.append('g')
      .attr('id', 'streamview-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
      .attr('width', width)
      .attr('height', height)
    g.selectAll('.stream-layer')
      .data(layers)
      .enter().append('path')
      .attr('class', 'stream-layer')
      .attr('d', area)
      .attr('stroke', '#E1F5C4')
      .attr('stroke-width', 0.1)
      .attr('fill', (d, i) => `url(#linear-gradient${i}`)
    // time axis
    const parseTime = d3.timeParse('%Y-%m-%d')  // string to Date
    const parseDate = d3.timeFormat('%Y-%m-%d')  // Date to string
    const timeData = datelist.map(d => parseTime(d))
    const timeScale = d3.scaleTime()
      .domain(d3.extent(timeData))
      .range([0, width])
    g.append('g')
      .attr('id', 'streamview-timeaxis')
      .attr('transform', `translate(0, ${streamHeight})`)
      .call(d3.axisBottom(timeScale))
    // highlight label
    const hintHeight = 4,
      hintWidth = timeScale(timeData[1])-timeScale(timeData[0])
    g.append('g')
      .attr('id', 'streamview-time-hint-g')
      .attr('transform', `translate(0, ${streamHeight+hintHeight/2})`)
      .selectAll('.hint')
      .data(datelist)
      .enter().append('rect')
      .attr('class', 'streamview-time-hint')
      .attr('x', d => timeScale(parseTime(d)))
      .attr('y', hintHeight/2)
      .attr('width', hintWidth)
      .attr('height', hintHeight)
      .style('fill', '#4682b4')
      .style('visibility', 'hidden')
    // mouse event
    let clicked = false
    const tooltip = d3.select('body').append('div')
      .attr('id', 'streamview-tooltip')
      .attr('class', 'streamview-tooltip')
      .style('visibility', 'hidden')
      .style('top', `${document.getElementById('streamview').offsetTop}px`)

    g.selectAll('.stream-layer')
      .attr('opacity', 1)
      .on('mouseover', (d, i) => {
        if(!clicked) {
          g.selectAll('.stream-layer').transition()
            .duration(250)
            .attr('opacity', (d, ii) => ii!=i?0.3:1)
        }
      })
      .on('mousemove', function(d, i) {
        if(!clicked) {
          const mousex = d3.mouse(this)[0],
            invertx = parseInt(xScale.invert(mousex)),
            date = timeScale.invert(mousex),
            kwsObj = matrix[invertx]
          const layer = `layer${i}`,
            score = kwsObj[layer],
            keyword = keywords[i][0]
          let tempSum = 0
          for(const key in kwsObj) {
            if(key=='x') {continue}
            tempSum += kwsObj[key]
          }
          let newsList = []
          let htmlContent = `<div class='date'>${parseDate(date)}</div><div class='selected'>${keywords[i][0]}: ${(score/tempSum*100).toFixed(2)}%</div>`
          const idx = datelist.indexOf(parseDate(date))
          for(let ii=0;ii<5;ii++) {
            const news = newsData[datelist[idx+ii]]
            if(news !== undefined) {
              newsList = newsList.concat(news)
            }
          }
          for(const news of newsList) {
            const title = news.title,
              content = news.content
            if(title.includes(keyword)) {
              htmlContent += `<div class='date'>${title}</div>`
              htmlContent += `<div class='selected'>${content}</div>`
            }
          }
          tooltip
            .style('left', `${mousex-document.getElementById('streamview').offsetLeft<=200?mousex+40+document.getElementById('streamview').offsetLeft:mousex-200+document.getElementById('streamview').offsetLeft}px`)
            .html(htmlContent)
            .style('visibility', 'visible')
          // interact with stateview
          d3.selectAll('.stateview-link').attr('opacity', 0.1)
          d3.selectAll('.stateview-node').each(function(d) {
            d3.select(this).attr('opacity', 1)
            if(d.date != parseDate(date)) {
              d3.select(this).attr('opacity', 0.1)
            }
          })
          // interact with global keyword view
          d3.selectAll('.global-keyword-link').each(function() {
            const linkId = d3.select(this).attr('id')
            if(linkId == `global-keyword-link-${keywords[i][0]}`) {
              d3.select(this).attr('stroke-width', '3px')
                .attr('stroke-opacity', 1)
            }
            else {
              d3.select(this).attr('stroke-width', '1px')
                .attr('stroke-opacity', 0.3)
            }
          })
        }
      })
      .on('mouseout', () => {
        if(!clicked) {
          g.selectAll('.stream-layer').transition()
            .duration(250)
            .attr('opacity', 1)
          tooltip.style('visibility', 'hidden')
          // interact with stateview
          d3.selectAll('.stateview-link').attr('opacity', 1)
          d3.selectAll('.stateview-node').attr('opacity', 1)
          // // interact with global keyword view
          d3.selectAll('.global-keyword-link').attr('stroke-width', '1px')
          d3.selectAll('.global-keyword-link').attr('stroke-opacity', 1)
        }
      })
    d3.select('#streamview-svg').on('click', function() {
      if(this==d3.event.target) {  // click empty area
        clicked = false
      }
      else {
        clicked = true
      }
    })
  }
  update() {
  }
}
