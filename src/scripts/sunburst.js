import * as d3 from 'd3'


export default class Sunburst{
  constructor(){
  }
  initScene(data) {
    const margin = {top: 40, right: 40, bottom: 10, left:40},
      width = window.innerWidth*0.8,
      height = window.innerHeight*0.6-70,
      radius = Math.min(width, height)/2.5,
      colorScale = ['#E3BA22', '#E58429', '#BD2D28', '#D15A86', '#8E6C8A',
        '#6B99A1', '#42A5B3', '#0F8C79', '#6BBBA1', '#5C8100'],
      bread = {w: 75, h: 30, s: 3, t:10}
    let totalSize = 0
    const svg = d3.select(document.getElementById('wordburstview')).append('svg')
      .attr('id', 'wordburst-svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
    const g = svg.append('g')
      .attr('id', 'wordburst-g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`)
    const partition = d3.partition()
      .size([2 * Math.PI, radius * radius])
    const arc = d3.arc()
      .startAngle(d => d.x0)
      .endAngle(d => d.x1)
      .innerRadius(d => Math.sqrt(d.y0))
      .outerRadius(d => Math.sqrt(d.y1))
    const json = buildHierarchy(data)
    createVisualization(json)
    // Main function to draw and set up the visualization, once we have the data.
    function createVisualization(json) {
    // Basic setup of page elements.
      initializeBreadcrumbTrail()
      // Bounding circle underneath the sunburst, to make it easier to detect
      // when the mouse leaves the parent g.
      g.append('circle')
        .attr('r', radius)
        .style('opacity', 0)
      // Turn the data into a d3 hierarchy and calculate the sums.
      const root = d3.hierarchy(json)
        .sum(d => d.size)
        .sort((a, b) => (b.value - a.value))
      // For efficiency, filter nodes to keep only those large enough to see.
      const nodes = partition(root).descendants()
        .filter(function(d) {
          return (d.x1 - d.x0 > 0.005)  // 0.005 radians = 0.29 degrees
        })

      const path = g.data([json]).selectAll('path')
        .data(nodes)
        .enter().append('svg:path')
        .attr('display', d => d.depth ? null : 'none')
        .attr('d', arc)
        .attr('fill-rule', 'evenodd')
        .style('fill', d => colorScale[d.data.name])
        .style('opacity', 1)
        .on('mouseover', mouseover)

      // Add the mouseleave handler to the bounding circle.
      d3.select('#container').on('mouseleave', mouseleave)
      // Get total size of the tree = value of root node from partition.
      totalSize = path.node().__data__.value
    }
    // Take a 2-column CSV and transform it into a hierarchical structure suitable
    // for a partition layout. The first column is a sequence of step names, from
    // root to leaf, separated by hyphens. The second column is a count of how
    // often that sequence occurred.
    function buildHierarchy(json) {
      const root = {'name': 'root', 'children': []}
      for (let i = 0; i < json.length; i++) {
        const sequence = json[i][0]
        const size = +json[i][1]
        if (isNaN(size)) { // e.g. if this is a header row
          continue
        }
        const parts = sequence.split('-')
        let currentNode = root
        for (let j = 0; j < parts.length; j++) {
          const children = currentNode['children']
          const nodeName = parts[j]
          let childNode
          if (j + 1 < parts.length) {
            // Not yet at the end of the sequence  move down the tree.
            let foundChild = false
            for (let k = 0; k < children.length; k++) {
              if (children[k]['name'] == nodeName) {
                childNode = children[k]
                foundChild = true
                break
              }
            }
            // If we don't already have a child node for this branch, create it.
            if (!foundChild) {
              childNode = {'name': nodeName, 'children': []}
              children.push(childNode)
            }
            currentNode = childNode
          }
          else {
            // Reached the end of the sequence  create a leaf node.
            childNode = {'name': nodeName, 'size': size}
            children.push(childNode)
          }
        }
      }
      return root
    }
  }
}
