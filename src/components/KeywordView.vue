<template>
  <div id="keywordview">
    <div id="keyword-tendency"></div>
    <div id="keyword-overview"></div>
  </div>
</template>

<script>
import Keywordlayout from '../scripts/keywordlayout'

export default {
  name: 'KeywordView',
  data() {
    return {
      kl: new Keywordlayout(),
    }
  },
  mounted() {
    this.eventHub.$on('initKeywordView', data => this.kl.initScene(data))
    this.eventHub.$on('switchKeywordShowGroups', opt => this.kl.switchShowGroups(opt))
  }
}
</script>

<style>
#keywordview {
  position: relative;
  float: left;
  -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
  filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) )
}
.keyword-text {
  font-family: "Times New Roman", Times, serif;
  font-weight: bold;
  font-size: 7px;
}
#keyword-tendency {
  position: relative;
  float:left;
  width: 250px; /*150+200*/
  height: 450px;
  overflow: auto;
}
#keyword-overview {
  position: relative;
  float: left;
  width: 650px;
  height: 450px;
  overflow: auto;
}
</style>
