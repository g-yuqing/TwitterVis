import * as sigma from 'sigma'

export default class Animation {
  constructor() {
    this.id = 0
    this.cache = {}
  }
  parseColor(val) {
    if (this.cache[val]) {
      return this.cache[val]
    }
    let result = [0, 0, 0]
    if (val.match(/^#/)) {
      val = (val || '').replace(/^#/, '')
      result = (val.length === 3) ?
        [
          parseInt(val.charAt(0) + val.charAt(0), 16),
          parseInt(val.charAt(1) + val.charAt(1), 16),
          parseInt(val.charAt(2) + val.charAt(2), 16)
        ] :
        [
          parseInt(val.charAt(0) + val.charAt(1), 16),
          parseInt(val.charAt(2) + val.charAt(3), 16),
          parseInt(val.charAt(4) + val.charAt(5), 16)
        ]
    } else if (val.match(/^ *rgba? *\(/)) {
      val = val.match(
        /^ *rgba? *\( *([0-9]*) *, *([0-9]*) *, *([0-9]*) *(,.*)?\) *$/
      )
      result = [
        +val[1],
        +val[2],
        +val[3]
      ]
    }
    this.cache[val] = {
      r: result[0],
      g: result[1],
      b: result[2]
    }
    return this.cache[val]
  }
  interpolateColors(c1, c2, p) {
    c1 = this.parseColor(c1)
    c2 = this.parseColor(c2)

    const c = {
      r: c1.r * (1 - p) + c2.r * p,
      g: c1.g * (1 - p) + c2.g * p,
      b: c1.b * (1 - p) + c2.b * p
    }
    return `rgb(${[c.r | 0, c.g | 0, c.b | 0].join(',')})`
  }
  animate(s, animate, options) {
    const o = options || {},
      id = ++this.id,
      duration = o.duration || s.settings('animationsTime'),
      easing = typeof o.easing === 'string' ?
        sigma.utils.easings[o.easing] :
        typeof o.easing === 'function' ?
          o.easing :
          sigma.utils.easings.quadraticInOut,
      start = sigma.utils.dateNow()
    let nodes

    if (o.nodes && o.nodes.length) {
      if (typeof o.nodes[0] === 'object') {
        nodes = o.nodes
      }
      else {
        nodes = s.graph.nodes(o.nodes) // argument is an array of IDs
      }
    }
    else {
      nodes = s.graph.nodes()
    }

    // Store initial positions:
    const startPositions = nodes.reduce((res, node) => {
      let k
      res[node.id] = {}
      for (k in animate)
        if (k in node)
          res[node.id][k] = node[k]
      return res
    }, {})

    s.animations = s.animations || Object.create({})
    this.kill(s)

    // Do not refresh edgequadtree during drag:
    let k,
      c
    for (k in s.cameras) {
      c = s.cameras[k]
      c.edgequadtree._enabled = false
    }

    //const interpolateColors = this.interpolateColors
    const step = () => {
      let p = (sigma.utils.dateNow() - start) / duration

      if (p >= 1) {
        nodes.forEach(node => {
          for (const k in animate)
            if (k in animate)
              node[k] = node[animate[k]]
        })
        // Allow to refresh edgequadtree:
        let k,
          c
        for (k in s.cameras) {
          c = s.cameras[k]
          c.edgequadtree._enabled = true
        }
        s.refresh()
        if (typeof o.onComplete === 'function')
          o.onComplete()
      }
      else {
        p = easing(p)
        nodes.forEach(node => {
          for (const k in animate)
            if (k in animate) {
              if (k.match(/color$/))
                node[k] = this.interpolateColors(startPositions[node.id][k], node[animate[k]],p)
              else
                node[k] = node[animate[k]] * p + startPositions[node.id][k] * (1 - p)
            }
        })
        s.refresh()
        s.animations[id] = requestAnimationFrame(step)
      }
    }
    step()
  }
  kill(s) {
    for(const k in (s.animations || {}))
      cancelAnimationFrame(s.animations[k])
    // Allow to refresh edgequadtree:
    let k,
      c
    for (k in s.cameras) {
      c = s.cameras[k]
      c.edgequadtree._enabled = true
    }
  }
}
