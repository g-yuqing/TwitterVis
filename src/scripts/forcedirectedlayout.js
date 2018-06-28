import * as Sigma from 'sigma'
import GPGPU from './gpgpu'
import clustering from 'density-clustering'


export default function drawForcelayout(data) {
  // check texture size
  const width = 1200,
    height = 600
  let text_size = 16
  const len = data.nodes.length + Math.floor(data.edges.length / 4)+1
  while(text_size*text_size < len) {
    text_size *= 2
  }
  const gpgpu = new GPGPU(text_size, text_size, data)
  gpgpu.calculation()
  const nodes = gpgpu.nodeData,
    edges = data.edges
  for(let i=0; i<edges.length; i++) {
    edges[i].id = i
    edges[i].color = '#eee'
  }
  const graph = {nodes: nodes, edges: edges}

  const container = document.getElementById('main-container')
  container.innerHTML = ''
  container.style.width = `${width}px`
  container.style.height = `${height}px`
  // clusterData()
  const s = new Sigma.sigma({
    graph: graph,
    container: container,
    settings: {
      maxNodeSize: 1.5,
      maxEdgeSize: 3,
    }
  })
  s.refresh()

  //
  // function clusterData() {
  //   console.log('start')
  //   const positions = this.gpgpu.nodePosition
  //   const dbscan = new clustering.DBSCAN()
  //   const minpts = 1,//Math.floor(positions.length/150),
  //     eps = 3
  //   const clusters = dbscan.run(positions, eps, minpts)
  //   const clusterNum = clusters.length
  //   console.log(clusterNum)
  //   console.log(clusters)
  //   const colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231',
  //     '#911eb4', '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080',
  //     '#e6beff', '#aa6e28', '#fffac8', '#800000', '#aaffc3', '#808000',
  //     '#ffd8b1', '#000080', '#808080', '#FFFFFF', '#000000']
  //   for(let i=0; i<clusterNum; i++) {
  //     for(const n of clusters[i]) {
  //       this.nodes[n].color = colors[i]
  //       this.nodes[n].cluster = i
  //     }
  //   }
  // }
}
