import * as Sigma from 'sigma'
import Animation from './animation'
import GPGPU from './gpgpu'
import clustering from 'density-clustering'


export default class Forcelayout {
  constructor() {
    this.width = window.innerWidth
    this.height = window.innerHeight
    this.animation = new Animation()
    this.graph = {}
  }
  initScene(data) {
    //check texture size
    let text_size = 16
    const len = data.nodes.length + Math.floor(data.edges.length / 4)+1
    while(text_size*text_size < len) {
      text_size *= 2
    }
    this.gpgpu = new GPGPU(text_size, text_size, data)
    this.gpgpu.calculation()
    this.nodes = this.gpgpu.nodeData
    this.edges = data.edges
    for(let i=0; i<this.edges.length; i++) {
      // this.edges[i].id = i
      this.edges[i].color = '#eee'
    }
    this.graph = {nodes: this.nodes, edges: this.edges}

    const container = document.getElementById('main-container')
    container.innerHTML = ''
    container.style.width = `${this.width}px`
    container.style.height = `${this.height}px`
    // this.clusterData()

    const s = new Sigma.sigma({
      graph: this.graph,
      container: container,
      settings: {
        maxNodeSize: 1.5,
        maxEdgeSize: 3,
      }
    })
    s.refresh()
    // this.saveToJSON()

    // this.graph = data
    // const container = document.getElementById('main-container')
    // container.innerHTML = ''
    // container.style.width = `${this.width}px`
    // container.style.height = `${this.height}px`
    // const s = new Sigma.sigma({
    //   graph: this.graph,
    //   container: container,
    //   settings: {
    //     maxNodeSize: 5,
    //     maxEdgeSize: 3,
    //   }
    // })
    // s.refresh()
  }
  saveToJSON() {
    const json_graph = JSON.stringify(this.graph)
    const a = document.createElement('a')
    const file = new Blob([json_graph], {type: 'application/json'})
    a.href = URL.createObjectURL(file)
    a.download = '2011.json'
    a.click()
  }
  clusterData() {
    console.log('start')
    const positions = this.gpgpu.nodePosition
    const dbscan = new clustering.DBSCAN()
    const minpts = 1,//Math.floor(positions.length/150),
      eps = 3
    const clusters = dbscan.run(positions, eps, minpts)
    const clusterNum = clusters.length
    console.log(clusterNum)
    console.log(clusters)
    const colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
      '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',
      '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000',
      '#ffd8b1', '#000080', '#808080', '#FFFFFF', '#000000']
    for(let i=0; i<clusterNum; i++) {
      for(const n of clusters[i]) {
        this.nodes[n].color = colors[i]
        this.nodes[n].cluster = i
      }
    }
  }
}
