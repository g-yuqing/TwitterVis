<template>
  <div id="app">
    <div id="keyword-bar">
      <el-tag
        :key="tag"
        v-for="tag in dynamicTags"
        closable
        :disable-transitions="false"
        @close="handleClose(tag)">
        {{tag}}
      </el-tag>
      <el-input
        class="input-new-tag"
        v-if="inputVisible"
        v-model="inputValue"
        ref="saveTagInput"
        size="small"
        @keyup.enter.native="handleInputConfirm"
        @blur="handleInputConfirm">
      </el-input>
      <el-button v-else class="button-new-tag" size="small" @click="showInput">+ New Tag</el-button>
    </div>
    <layout></layout>
  </div>
</template>

<script>
import Layout from './components/LayoutView'


export default {
  name: 'App',
  components: {
    layout: Layout,
  },
  data: () => ({
    dynamicTags: ['原発', '事故', '避難', '放射能'],
    inputVisible: false,
    inputValue: ''
  }),
  mounted() {
    this.loadData()
      .then(dataset => {
        this.graphData = dataset
        this.drawLayout()
      })
  },
  watch: {
    dynamicTags(val) {
      this.eventHub.$emit('updateLayoutScene', this.dynamicTags)
    }
  },
  methods: {
    async loadData() {
      const res = await fetch('../static/layout.json')
      const graphData = await res.json()
      return graphData
    },
    // layout methods
    drawLayout() {
      // document.getElementById('layout').innerHTML = ''
      this.eventHub.$emit('initLayoutScene', this.graphData, this.dynamicTags)
    },
    // tag methods
    handleClose(tag) {
      this.dynamicTags.splice(this.dynamicTags.indexOf(tag), 1)
    },
    showInput() {
      this.inputVisible = true;
      this.$nextTick(_ => {
      this.$refs.saveTagInput.$refs.input.focus()
      })
    },
    handleInputConfirm() {
      let inputValue = this.inputValue
      if (inputValue) {
        this.dynamicTags.push(inputValue)
      }
      this.inputVisible = false
      this.inputValue = ''
    }
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
.el-tag + .el-tag {
  margin-left: 10px;
}
.button-new-tag {
  margin-left: 10px;
  height: 32px;
  line-height: 30px;
  padding-top: 0;
  padding-bottom: 0;
}
.input-new-tag {
  width: 90px;
  margin-left: 10px;
  vertical-align: bottom;
}
</style>
