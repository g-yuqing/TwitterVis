export default class GPGPU {
  constructor(tex_width, tex_height, data) {
    this.iter = 600
    this.win_width = window.innerWidth
    this.win_height = window.innerHeight
    this.tex_width = tex_width
    this.tex_height = tex_height
    this.nodes = data.nodes
    this.edges = data.edges
    this.nodes_count = this.nodes.length
    this.edges_count = this.edges.length
    this.len = this.tex_height * this.tex_width * 4 // 4 channels
    this.uniforms = {
      tex_size: this.tex_width*this.tex_height,
      max_vertex_deg: -1,
      node_count: this.nodes_count,
      k_2: 1/(this.nodes_count+1)*1000,
      k: Math.sqrt(this.win_height/(this.nodes_count+1))/7,
      gravity: 0.1,
      speed: 0.11,
      max_displace: 1,
    }
    this.positions = []
    // gl configuration
    this.canvas = document.createElement('canvas')
    this.canvas.width = this.win_width
    this.canvas.height = this.win_height
    this.gl = this.canvas.getContext('webgl')
    //enable gl.FLOAT
    const gl_float_enable = this.gl.getExtension('OES_texture_float')
    if(!gl_float_enable) {
      console.log('gl.FLOAT is not support')
      return
    }
  }
  calculation() {
    const tex_array = new Float32Array(this.setDataArray())
    //vertex shader
    const vsshader = this.gl.createShader(this.gl.VERTEX_SHADER)
    this.gl.shaderSource(vsshader, require('../shaders/vertex.vert'))
    this.gl.compileShader(vsshader)
    if(!this.gl.getShaderParameter(vsshader, this.gl.COMPILE_STATUS)) {
      throw new Error(this.gl.getShaderInfoLog(vsshader))
    }
    //fragment shader
    const fsshader = this.gl.createShader(this.gl.FRAGMENT_SHADER)
    this.gl.shaderSource(fsshader, require('../shaders/fragment.frag'))
    this.gl.compileShader(fsshader)
    if(!this.gl.getShaderParameter(fsshader, this.gl.COMPILE_STATUS)) {
      throw new Error(this.gl.getShaderInfoLog(fsshader))
    }
    //program
    this.program = this.gl.createProgram()
    this.gl.attachShader(this.program, vsshader)
    this.gl.attachShader(this.program, fsshader)
    this.gl.linkProgram(this.program)
    if(!this.gl.getProgramParameter(this.program, this.gl.LINK_STATUS)) {
      throw new Error(this.gl.getProgramInfoLog(this.program))
    }
    this.gl.useProgram(this.program)

    //set attribute
    this.vertices = new Float32Array([-1.0, 1.0, 0.0, 0.0, 1.0,
      -1.0, -1.0, 0.0, 0.0, 0.0,
      1.0, 1.0, 0.0, 1.0, 1.0,
      1.0, -1.0, 0.0, 1.0, 0.0])
    const vbo = this.gl.createBuffer()
    this.gl.bindBuffer(this.gl.ARRAY_BUFFER, vbo)
    this.gl.bufferData(this.gl.ARRAY_BUFFER, this.vertices, this.gl.STATIC_DRAW)

    this.gl.vertexAttribPointer(0, 3, this.gl.FLOAT, this.gl.FALSE, 5*4, 0)
    this.gl.enableVertexAttribArray(0)

    this.gl.vertexAttribPointer(1, 2, this.gl.FLOAT, this.gl.FALSE, 5*4, 3*4)
    this.gl.enableVertexAttribArray(1)

    this.gl.bindAttribLocation(this.program, 0, 'position')
    this.gl.bindAttribLocation(this.program, 1, 'textureCoord')
    //set uniforms
    this.setUniforms()
    //texture
    this.ping = this.initBufferframeTexture(tex_array)
    this.pong = this.initBufferframeTexture(tex_array)

    this.gl.viewport(0, 0, this.tex_width, this.tex_height)

    for(let i=0; i<this.iter; i++) {
      //clear
      this.gl.activeTexture(this.gl.TEXTURE0)
      this.gl.bindTexture(this.gl.TEXTURE_2D, null)
      this.gl.bindFramebuffer(this.gl.FRAMEBUFFER, null)

      this.gl.bindFramebuffer(this.gl.FRAMEBUFFER, this.pong.frame)
      this.gl.activeTexture(this.gl.TEXTURE0)
      this.gl.bindTexture(this.gl.TEXTURE_2D, this.ping.tex)
      //calculate
      this.gl.drawArrays(this.gl.TRIANGLE_STRIP, 0, 4)
      //swap
      const temp = this.ping
      this.ping = this.pong
      this.pong = temp
    }
    this.readTexture()
  }
  setDataArray() {
    const data_array = []
    const src_tar = []
    for(let i=0; i<this.nodes_count; i++) {
      data_array.push(Math.random())
      data_array.push(Math.random())
      data_array.push(0)
      data_array.push(0)
      src_tar.push([])
    }
    for(let i=0; i<this.edges_count; i++) {
      const edge = this.edges[i]
      src_tar[edge.source].push(edge.target)
      src_tar[edge.target].push(edge.source)
    }
    for(let i=0; i<this.nodes_count; i++) {
      const offset = data_array.length
      const targets = src_tar[i]
      data_array[i*4+2] = offset
      data_array[i*4+3] = targets.length
      this.uniforms.max_vertex_deg = Math.max(this.uniforms.max_vertex_deg, targets.length)
      for(let j=0; j<targets.length; j++) {
        data_array.push(+targets[j])
      }
    }
    while(data_array.length < this.len) {
      data_array.push(0)
    }
    return data_array
  }
  initBufferframeTexture(tex_array) {
    const texture = this.gl.createTexture()
    this.gl.bindTexture(this.gl.TEXTURE_2D, texture)
    this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MIN_FILTER, this.gl.NEAREST)
    this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MAG_FILTER, this.gl.NEAREST)
    this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_WRAP_S, this.gl.CLAMP_TO_EDGE)
    this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_WRAP_T, this.gl.CLAMP_TO_EDGE)
    this.gl.texImage2D(this.gl.TEXTURE_2D, 0, this.gl.RGBA, this.tex_width, this.tex_height,
      0, this.gl.RGBA, this.gl.FLOAT, tex_array)

    const framebuffer = this.gl.createFramebuffer()
    this.gl.bindFramebuffer(this.gl.FRAMEBUFFER, framebuffer)
    this.gl.framebufferTexture2D(this.gl.FRAMEBUFFER, this.gl.COLOR_ATTACHMENT0,
      this.gl.TEXTURE_2D, texture, 0)
    const status = this.gl.checkFramebufferStatus(this.gl.FRAMEBUFFER)
    if(status != this.gl.FRAMEBUFFER_COMPLETE) {
      switch(status) {
      case this.gl.FRAMEBUFFER_UNSUPPORTED:
        console.log('Framebuffer is unsupported')
        break
      case this.gl.FRAMEBUFFER_INCOMPLETE_ATTACHMENT:
        console.log('Framebuffer incomplete attachment')
        break
      case this.gl.FRAMEBUFFER_INCOMPLETE_DIMENSIONS:
        console.log('Framebuffer incomplete (missmatched) dimensions')
        break
      case this.gl.FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT:
        console.log('Framebuffer incomplete missing attachment')
        break
      default:
        console.log(`Unexpected framebuffer status: ${status}`)
      }
    }
    const result = {frame: framebuffer, tex: texture}
    //clear
    this.gl.bindTexture(this.gl.TEXTURE_2D, null)
    this.gl.bindFramebuffer(this.gl.FRAMEBUFFER, null)
    return result
  }
  readTexture() {
    const result = new Float32Array(this.len)
    this.gl.readPixels(0, 0, this.tex_width, this.tex_height, this.gl.RGBA, this.gl.FLOAT, result)
    for(let i=0; i<this.nodes.length; i++) {
      // this.nodes[i].id = this.nodes[i].name
      const x = result[4*i]
      const y = result[4*i+1]
      this.nodes[i].x = x
      this.nodes[i].y = y
      this.nodes[i].size = 1
      this.nodes[i].color = '#e6194b'
      // this.nodes[i].size = this.nodes[i].name[0] == 'S' ? 5 : 2
      // this.nodes[i].color = this.nodes[i].name[0] == 'S' ? '#e6194b' : '#A59B9B'
      // this.nodes[i].cluster = -1
      this.positions.push([x, y])
    }
  }
  setUniforms() {
    //set uniform
    const unilocation = []
    unilocation[0] = this.gl.getUniformLocation(this.program, 'max_vertex_deg')
    this.gl.uniform1i(unilocation[0], this.uniforms.max_vertex_deg)
    unilocation[1] = this.gl.getUniformLocation(this.program, 'node_count')
    this.gl.uniform1i(unilocation[1], this.uniforms.node_count)
    unilocation[2] = this.gl.getUniformLocation(this.program, 'k_2')
    this.gl.uniform1f(unilocation[2], this.uniforms.k_2)
    unilocation[3] = this.gl.getUniformLocation(this.program, 'k')
    this.gl.uniform1f(unilocation[3], this.uniforms.k)
    unilocation[4] = this.gl.getUniformLocation(this.program, 'gravity')
    this.gl.uniform1f(unilocation[4], this.uniforms.gravity)
    unilocation[5] = this.gl.getUniformLocation(this.program, 'speed')
    this.gl.uniform1f(unilocation[5], this.uniforms.speed)
    unilocation[6] = this.gl.getUniformLocation(this.program, 'max_displace')
    this.gl.uniform1f(unilocation[6], this.uniforms.max_displace)
    unilocation[7] = this.gl.getUniformLocation(this.program, 'tex_width')
    this.gl.uniform1i(unilocation[7], this.tex_width)
    unilocation[8] = this.gl.getUniformLocation(this.program, 'tex_height')
    this.gl.uniform1i(unilocation[8], this.tex_height)
  }
  get nodePosition() {
    return this.positions
  }
  get nodeData() {
    return this.nodes
  }
}
