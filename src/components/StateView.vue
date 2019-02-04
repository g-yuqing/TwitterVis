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
    this.eventHub.$on('initStateView', (stateData, keywordData, newsData) => this.sl.initScene(stateData, keywordData, newsData))
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
  width: 450px;
  height: 540px;
}
.stateview-text {
  font-family: "Times New Roman", Times, serif;
  font-weight: bold;
  font-size: 10px;
}
.stateview-node-text:hover text {
  display: inline;
}
.stateview-node-text text {
  display: none;
  font: 10px sans-serif;
}
/* .stateview-link-text:hover text {
  display: inline;
}
.stateview-link-text text {
  display: none;
  font: 10px sans-serif;
}
.stateview-tooltip {
  background-color: hsla(0,0%,100%,0.7);
  padding: 10px;
  border-radius: 5px;
  font-size: 7px;
  width: 50px;
  height: 50px;
  position: absolute;
  z-index: 20;
}
.stateview-tooltip .date {
  font-size: 12px;
  margin-bottom: 2px;
} */
</style>
