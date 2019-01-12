<template>
  <div id="stateview"></div>
</template>

<script>
import Statelayout from '../scripts/statelayout'

export default {
  name: 'StateView',
  data() {
    return {
      sl: new Statelayout(),
    }
  },
  mounted() {
    this.eventHub.$on('initStateView', (stateData, keywordData) => this.sl.initScene(stateData, keywordData))
    this.eventHub.$on('switchStateDimension', opt => this.sl.switchDimension(opt))
    this.eventHub.$on('switchStateShowGroups', opt => this.sl.switchShowGroups(opt))
  }
}
</script>

<style>
#stateview {
  position: relative;
  float: left;
  -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
  filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) );
  width: 500px;
  height: 600px;
}
.stateview-text {
  font-family: "Times New Roman", Times, serif;
  font-weight: bold;
  font-size: 10px;
}
</style>
