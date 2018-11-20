import * as d3 from 'd3'
import axios from 'axios'
import Topiclayout from './topiclayout'


export default class Keywordlayout {
  constructor() {
  }
  initScene(dataset) {
    // dataset: [{date: '', kwscore: [['kw', 'score'], ['kw', 'score']]}]
    // changed word : #99B898 else: #FECEAB
    // leap date: #E84A5F else: #2A3633B
    const margin = {top: 40, right: 40, bottom: 10, left:40},
      width = document.getElementById('keywordview').offsetWidth-margin.left-margin.right,
      height = document.getElementById('keywordview').offsetHeight-margin.top-margin.bottom,
      titleHeight = 20,
      graphHeight = height - titleHeight,
      datelist = dataset.map(d => d.date),
      tl = new Topiclayout()
    // empty previous visualization
    document.getElementById('keywordview').innerHTML = ''
    // visualize
    const svg = d3.select(document.getElementById('keywordview')).append('svg')
      .attr('id', 'keyword-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const titleG = svg.append('g')
      .attr('id', 'keyword-title-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
      .attr('width', width)
      .attr('height', titleHeight)
    const graphG = svg.append('g')
      .attr('id', 'keyword-graph-g')
      .attr('transform', `translate(${margin.left}, ${margin.top+titleHeight})`)
      .attr('width', width)
      .attr('height', graphHeight)
    const xScale = d3.scalePoint()
      .domain(datelist)
      .range([0, width])
    const yScale = d3.scalePoint()
      .domain(d3.range(dataset[0].kwscore.length))
      .range([graphHeight, 0])

    // parepare title data
    const titleData = datelist.map(d => {
      return {
        x: xScale(d),
        y: 0,
        text: d,
        color: '#2A3633B'
      }
    })
    // draw title
    titleG.append('g').selectAll ('.title').data(titleData)
      .enter().append('text')
      .text(d => d.text)
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('fill', d => d.color)
      .style('text-anchor', 'middle')
      .style('font-size', '10px')

    // prepare node & link data
    const nodes = [],
      wordCoords = {}  // {word: [[date1, idx1], [date2, idx2]]}
    let links = []
    // init wordCoords
    for(const data of dataset) {
      const date = data.date,
        kwscoreList = data.kwscore
      for(const i in kwscoreList) {
        const kwscore = kwscoreList[i],
          kw = kwscore[0],
          // score = kwscore[1],
          idx = i
        if(kw in wordCoords) {
          wordCoords[kw].push([date, idx])
        }
        else {
          wordCoords[kw] = [[date, idx]]
        }
      }
    }
    // init nodes & links
    for(const [word, coords] of Object.entries(wordCoords)) {  // coords: [date, idx]
      let color = '#E84A5F',  // leap color
        tempLinks = []
      const wordlinks = []
      const worddates = coords.map(d => d[0])
      for(const date of datelist) {
        const i = worddates.indexOf(date)
        if(i != -1) {
          // set nodes & links
          const  coord = coords[i],
            x = xScale(coord[0]),
            y = yScale(coord[1])
          nodes.push({x: x, y: y, word: word, color: color})
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
      links = links.concat(wordlinks)
    }
    // link
    const line = d3.line()
      .x(d => d.x)
      .y(d => d.y)
      .curve(d3.curveMonotoneX)
    for(const link of links) {
      graphG.append('g').append('path')
        .datum(link)
        .attr('class', 'keyword-link')
        .attr('stroke-width', '1px')
        .attr('stroke', '#A8A7A7')
        .attr('fill', 'none')
        .attr('d', line)
    }
    // draw node
    graphG.append('g').selectAll('.dot').data(nodes)
      .enter().append('text')
      .attr('class', 'keyword-node')
      .text(d => d.word)
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('fill', d => d.color)
      .style('text-anchor', 'middle')
      .style('font-size', '9px')
      .on('mouseover', d => {
        d3.selectAll('.keyword-node').each(function(dd) {
          if(dd.word != d.word) {
            d3.select(this).style('opacity', 0.1)
          }
        })
        d3.selectAll('.keyword-link').each(function(dd) {
          const wordlist = dd.map(ddd => ddd.word)
          if(!(wordlist.includes(d.word))) {
            d3.select(this).style('stroke-opacity', 0.1)
          }
        })
      })
      .on('mouseout', () => {
        d3.selectAll('.keyword-node').style('opacity', null)
        d3.selectAll('.keyword-link').style('stroke-opacity', null)
      })
      .on('click', d => {
        const params = new URLSearchParams()
        params.set('keyword', d.word)
        for(const date of datelist) {
          params.append('dates', date)
        }
        const url = `http://0.0.0.0:5000/topic/${params.toString()}`
        axios.get(url)
          .then(res => {
            const topicGraph = res.data
            console.log('retreive topic graph data successfully')
            tl.initScene(topicGraph)
          })
      })
  }
}
