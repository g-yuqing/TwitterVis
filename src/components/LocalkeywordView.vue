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
    this.eventHub.$on('initLocalKeywordView', (keywordData, newsData, dateHull) => this.lk.initScene(keywordData, newsData, dateHull))
  }
}
</script>

<style>
#local-keyword {
  position: relative;
  float: left;
  /* float: right; */
  -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
  filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) );
  width: 100%;
  height: 380px;
  /* overflow: auto; */
  overflow-x: auto;
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
.local-keyword-tooltip {
  background-color: hsla(0,0%,100%,0.7);
  padding: 10px;
  border-radius: 5px;
  font-weight: bold;
  font-size: 10px;
	width: 80px;
  height: 7px;
  position: absolute;
  z-index: 20;
}
</style>
