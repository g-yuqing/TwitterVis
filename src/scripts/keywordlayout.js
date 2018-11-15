import * as d3 from 'd3'


export default class Keywordlayout {
  constructor() {
  }
  initScene(dataset) {
    // dataset: [{date: '', kwscore: [['kw', 'score'], ['kw', 'score']]}]
    // changed word : #99B898 else: #FECEAB
    // leap date: #E84A5F else: #2A3633B
    const margin = {top: 70, right: 50, bottom: 10, left:40},
      width = window.innerWidth*0.8,
      height = 400,
      datelist = dataset.map(d => d.date)
    const svg = d3.select(document.getElementById('keywordview')).append('svg')
      .attr('id', 'keyword-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const titleG = svg.append('g')
      .attr('id', 'keyword-title-g')
      .attr('transform', `translate(${margin.left}, 40)`)
    const graphG = svg.append('g')
      .attr('id', 'keyword-graph-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
    const xScale = d3.scalePoint()
      .domain(datelist)
      .range([0, width])
    const yScale = d3.scalePoint()
      .domain(d3.range(dataset[0].kwscore.length))
      .range([height, 0])


    const nodes = [],
      links = [],
      wordCoords = {}  // {word: [[date1, idx1], [date2, idx2]]}
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
      // init nodes
      const link = []
      for(const coord of coords) {
        const x = xScale(coord[0]),
          y = yScale(coord[1])
        nodes.push({
          x: x,
          y: y,
          word: word,
          color: '#E84A5F'
        })
        link.push({
          x: x,
          y: y
        })
      }
      // init links
      links.push(link)
    }

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
    const kwTitle = titleG.append('g').selectAll ('.title').data(titleData)
      .enter().append('text')
      .text(d => d.text)
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('fill', d => d.color)
      .style('text-anchor', 'middle')
      .style('font-size', '10px')

    // link
    const line = d3.line()
      .x(d => d.x)
      .y(d => d.y)
      .curve(d3.curveMonotoneX)
    // const kwLink = g.append('g').selectAll('.link').data(links)
    //   .enter().append('path')
    //   .attr('id', (d, i) => `keyword-link${i}`)
    //   .attr('class', 'keyword-link')
    //   .attr('stroke-width', '1px')
    //   .attr('stroke', '#FECEAB')
    //   .attr('fill', 'none')
    //   .attr('d', d => `M${d.src.x},${d.src.y}
    //                    L${d.dst.x},${d.dst.y}`)
    for(const link of links) {
      graphG.append('g').append('path')
        .datum(link)
        .attr('class', 'keyword-link')
        .attr('stroke-width', '1px')
        .attr('stroke', '#FECEAB')
        .attr('fill', 'none')
        .attr('d', line)
    }
    // draw node
    const kwNode = graphG.append('g').selectAll('.dot').data(nodes)
      .enter().append('g')
    kwNode.append('text')
      .text(d => d.word)
      .attr('x', d => d.x)
      .attr('y', d => d.y)
      .attr('fill', d => d.color)
      .style('text-anchor', 'middle')
      .style('font-size', '9px')
  }
}
