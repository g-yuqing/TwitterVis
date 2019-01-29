import * as d3 from 'd3'
import * as cola from 'webcola'
// import Sunburst from 'sunburst-chart'


export default class Topiclayout {
  constructor() {
  }
  initScene(graph, wordText) {
    const margin = {top: 10, right: 10, bottom: 10, left:20},
      width = document.getElementById('topicview').offsetWidth-margin.left-margin.right,
      height = (document.getElementById('topicview').offsetHeight-margin.top-margin.bottom)
    const fontScale = d3.scaleLinear()
      .range([7, 15])
      .domain(d3.extent(graph.nodes, d => d.tf))
    const xScale = d3.scaleLinear()
      // .range([0, width-20])
      .range([width-20, 0])
    const yScale = d3.scaleLinear()
      .range([height-20, 0])
    // empty previous visualization
    document.getElementById('topicview').innerHTML = ''
    // visualize
    const tweetDiv = d3.select(document.getElementById('tweetview')).append('div')
      .attr('id', 'tweetview-div')
      .attr('class', 'tweetview')
    const svg = d3.select(document.getElementById('topicview')).append('svg')
      .attr('id', 'topic-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const graphG = svg.append('g')
      .attr('id', 'topic-g')
      .attr('width', width)
      .attr('height', height)
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
    const d3cola = cola.d3adaptor(d3)
      .avoidOverlaps(true)
      .flowLayout('x', 25)
      .size([width, height])
      .nodes(graph.nodes)
      .links(graph.links)
      .constraints(graph.constraints)
      .symmetricDiffLinkLengths(25)
      // .jaccardLinkLengths(30,0.7)
      .start(10, 20, 20)
    const link = graphG.append('g').selectAll('.link')
      .data(graph.links)
      .enter().append('path')
      .attr('class', 'topic-link')
      .attr('stroke', '#A8A7A7')
      .attr('fill', 'none')
      .style('stroke-opacity', 0.7)
      .on('click', d => {
        console.log(d.source.word, d.target.word)
      })
    graph.nodes.forEach(d => {
      d.width = 10*d.word.length,
      d.height = 10
    })
    const node = graphG.append('g').selectAll('.node')
      .data(graph.nodes)
      .enter().append('rect')
      .attr('class', 'topic-node')
      .attr('width', d => d.width)
      .attr('height', d => d.height)
      .style('fill', 'none')
      .call(d3cola.drag)
    const label = graphG.append('g').selectAll('.label')
      .data(graph.nodes)
      .enter().append('text')
      .attr('class', 'topic-label')
      .text(d => d.word)
      .attr('fill', d => d.color)
      .style('font-size', d => `${fontScale(d.tf/2)}px`)
      .call(d3cola.drag)
      .on('click', function(d) {
        // empty
        document.getElementById('tweetview-div').innerHTML = ''
        d3.selectAll('.topic-label').attr('stroke', null)
        // init
        const tempText = []
        const tweetData = []
        wordText.forEach(dd => {
          if(dd.words.includes(d.word) && !tempText.includes(dd.words.toString())) {
            tweetData.push({
              text: dd.text,
              count: dd.count})
            tempText.push(dd.words.toString())
          }
        })
        tweetData.sort((a, b) => (a.count < b.count) ? 1 : ((b.count < a.count) ? -1 : 0))
        d3.select(this).attr('stroke', '#99B898')

        let htmlContent = `<div class='tweet'>Tweet</div><div class='count'>keyword: ${d.word} - ${tweetData.length} tweets</div>`
        tweetData.forEach(td => {
          htmlContent += `<div class='count'>・retweet count: ${td.count}</div><div class='tweet'>${td.text}</div>`
        })
        tweetDiv.html(htmlContent)
        // const tableWidth = (width + margin.left + margin.right)*1.5,
        //   tableHeight = tweetData.length * 20
        // const tweetSvg = d3.select(document.getElementById('tweetview')).append('svg')
        //   .attr('id', 'tweet-svg')
        //   .attr('width', tableWidth)
        //   .attr('height', tableHeight)
        // const tweetG = tweetSvg.append('g')
        //   .attr('id', 'topic-g')
        //   .attr('width', tableWidth)
        //   .attr('height', tableHeight)
        //   .attr('transform', `translate(${margin.left}, ${margin.top})`)
        // tweetG
        //   .selectAll('.tweet')
        //   .data(tweetData)
        //   .enter()
        //   .append('text')
        //   .attr('class', 'tweet-text')
        //   .text(d => d.count)
        //   .attr('x', 0)
        //   .attr('y', (d, i) => i*25)
        //   .style('font-size', '10px')
        // tweetG
        //   .selectAll('.tweet')
        //   .data(tweetData)
        //   .enter().append('text')
        //   .attr('class', 'tweet-text')
        //   .text(d => d.text)
        //   .attr('x', 30)
        //   .attr('y', (d, i) => i*25)
        //   .style('font-size', '10px')
      })
    d3cola.on('tick', function() {
      xScale.domain(d3.extent(graph.nodes, d => d.x))
      yScale.domain(d3.extent(graph.nodes, d => d.y))
      link.attr('d', d => `M${xScale(d.source.x)},${yScale(d.source.y)}L${xScale(d.target.x)},${yScale(d.target.y)}`)
      node.attr('x', d => xScale(d.x-d.width/2))
        .attr('y', d => yScale(d.y-d.height/2))
      label.attr('x', d => xScale(d.x))
        .attr('y', d => yScale(d.y+d.height/4))
    })
  }
  // createBarChart(data, svg, offset) {
  //   // data: [{date: count}, {}]
  //   const width = 100,
  //     height = 10,
  //     datelist = data.datelist
  //   const xScale = d3.scaleBand()
  //     .domain(datelist[0], datelist[datelist.length-1])
  //     .range([0, width])
  //     .paddingInner(0.01)
  //   const xAxis = d3.axisBottom()
  //     .scale(xScale)
  //   const yScale = d3.scaleLinear()
  //     .domain(d3.extent(data, d=>d.rtc))
  //     .range([height, 0])
  //   const chartG = svg.append('g')
  //     .attr('transform', `translate(0, ${offset})`)
  //   chartG.append('g')
  //     .attr('class', 'rt-chart-axis')
  //     .call(xAxis)
  //   chartG.selectAll('.rt-chart-bar')
  //     .data(data)
  //     .enter().append('rect')
  //     .attr('class', 'rt-chart-bar')
  //     .attr('x', d => xScale(d.date))
  //     .attr('width', xScale.bandwidth())
  //     .attr('y', d => yScale(d.count))
  //     .attr('height', d => height - yScale(d.count))
  // }
}
