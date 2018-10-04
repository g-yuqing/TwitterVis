// import * as d3 from 'd3'

export default class NodeChart {
  constructor() {
    this.DEFAULT_OPTIONS = {
      radius: 5,
      outerStrokeWidth: 10,
      parentNodeColor: 'blue',
      showPieChartBorder: true,
      pieChartBorderColor: 'white',
      pieChartBorderWidth: '1',
      showLabelText: false,
      labelText: 'text',
      labelColor: 'blue',
      circleClass: 'tsne-circle'
    }
    this.color = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
      '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',
      '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000',
      '#ffd8b1', '#000080', '#808080', '#FFFFFF', '#000000']
  }
  getOptionOrDefault(key, options, defaultOptions) {
    defaultOptions = defaultOptions || this.DEFAULT_OPTIONS
    if (options && key in options) {
      return options[key]
    }
    return defaultOptions[key]
  }

  drawParentCircle(nodeElement, options) {
    const outerStrokeWidth = this.getOptionOrDefault('outerStrokeWidth', options)
    const radius = this.getOptionOrDefault('radius', options)
    const parentNodeColor = this.getOptionOrDefault('parentNodeColor', options)
    const parentCircleClass = this.getOptionOrDefault('circleClass', options)

    nodeElement.insert('circle')
      .attr('id', 'parent-pie')
      .attr('class', parentCircleClass)
      .attr('r', radius)
      .attr('fill', parentNodeColor)
      .attr('stroke', parentNodeColor)
      .attr('stroke-width', outerStrokeWidth)
  }

  drawPieChartBorder(nodeElement, options) {
    const radius = this.getOptionOrDefault('radius', options)
    const pieChartBorderColor = this.getOptionOrDefault('pieChartBorderColor', options)
    const pieChartBorderWidth = this.getOptionOrDefault('pieChartBorderWidth', options)
    const pieChartCircleClass = this.getOptionOrDefault('circleClass', options)

    nodeElement.insert('circle')
      .attr('r', radius)
      .attr('class', pieChartCircleClass)
      .attr('fill', 'transparent')
      .attr('stroke', pieChartBorderColor)
      .attr('stroke-width', pieChartBorderWidth)
  }

  drawPieChart(nodeElement, percentages, options) {
    const radius = this.getOptionOrDefault('radius', options)
    const halfRadius = radius / 2
    const halfCircumference = 2 * Math.PI * halfRadius
    const halfCircleClass = this.getOptionOrDefault('circleClass', options)

    let percentToDraw = 0
    for (const p in percentages) {
      percentToDraw += percentages[p].percent

      nodeElement.insert('circle', '#parent-pie + *')
        .attr('r', halfRadius)
        .attr('class', halfCircleClass)
        .attr('fill', 'transparent')
        .style('stroke', this.color[percentages[p].color])
        .style('stroke-width', radius)
        .style('stroke-dasharray', `${halfCircumference * percentToDraw / 100} ${halfCircumference}`)
    }
  }

  drawTitleText(nodeElement, options) {
    const radius = this.getOptionOrDefault('radius', options)
    const text = this.getOptionOrDefault('labelText', options)
    const color = this.getOptionOrDefault('labelColor', options)
    nodeElement.append('text')
      .text(String(text))
      .attr('fill', color)
      .attr('dy', radius * 2)
  }

  drawNodePie(nodeElement, percentages, options) {
    this.drawParentCircle(nodeElement, options)
    if (!percentages) return
    this.drawPieChart(nodeElement, percentages, options)
    const showPieChartBorder = this.getOptionOrDefault('showPieChartBorder', options)
    if (showPieChartBorder) {
      this.drawPieChartBorder(nodeElement, options)
    }
    const showLabelText = this.getOptionOrDefault('showLabelText', options)
    if (showLabelText) {
      this.drawTitleText(nodeElement, options)
    }
  }


}
