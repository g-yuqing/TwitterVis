<template>
  <div id="global-keyword"></div>
</template>

<script>
import GlobalKeyword from '../scripts/globalkeyword'

export default {
  name: 'GlobalKeywordView',
  data() {
    return {
      gk: new GlobalKeyword(),
    }
  },
  mounted() {
    this.eventHub.$on('initGlobalKeywordView', (stateData, keywordData) => this.gk.initScene(stateData, keywordData))
  }
}
</script>

<style>
#global-keyword {
  position: relative;
  float:left;
  -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
  filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) );
  width: 60%;
  height: 220px;
  overflow: auto;
}
.global-keyword-text {
  font-family: "Times New Roman", Times, serif;
  font-weight: bold;
  font-size: 7px;
}
</style>
