<template>
  <div id="local-keyword"></div>
</template>

<script>
import LocalKeyword from '../scripts/localkeyword'

export default {
  name: 'LocalKeywordView',
  data() {
    return {
      lk: new LocalKeyword(),
    }
  },
  mounted() {
    this.eventHub.$on('initKeywordView', data => this.lk.initScene(data))
    this.eventHub.$on('switchKeywordShowGroups', opt => this.lk.switchShowGroups(opt))
  }
}
</script>

<style>
#local-keyword {
  position: relative;
  float: left;
  -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
  filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) );
  width: 1150px;
  height: 600px;
  overflow: auto;
}
.local-keyword-text {
  font-family: "Times New Roman", Times, serif;
  font-weight: bold;
  font-size: 7px;
}
.local-keyword-node {
  font-family: "Times New Roman", Times, serif;
  font-weight: bold;
  font-size: 7px;
}
</style>
