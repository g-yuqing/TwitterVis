import * as Sigma from 'sigma'
import Animation from './animation'
import GPGPU from './gpgpu'


export default class Forcelayout {
  constructor() {
    this.width = window.innerWidth*0.5
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
      this.edges[i].id = i
      this.edges[i].color = '#eee'
    }
    this.graph = {nodes: this.nodes, edges: this.edges}

    const container = document.getElementById('main-container')
    container.innerHTML = ''
    container.style.width = `${this.width}px`
    container.style.height = `${this.height}px`

    const s = new Sigma.sigma({
      graph: this.graph,
      container: container,
      settings: {
        maxNodeSize: 1.3,
        maxEdgeSize: 3,
      }
    })
    s.refresh()
  }
  saveToJSON() {
    const json_graph = JSON.stringify(this.graph)
    const a = document.createElement('a')
    const file = new Blob([json_graph], {type: 'application/json'})
    a.href = URL.createObjectURL(file)
    a.download = '2011.json'
    a.click()
  }
}
