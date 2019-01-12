<template>
  <div id="streamview"></div>
</template>

<script>
import Streamlayout from '../scripts/streamlayout'

export default {
  name: 'StreamView',
  data() {
    return {
      sl: new Streamlayout(),
    }
  },
  mounted() {
    this.eventHub.$on('initStreamView', (stateData, keywordData) => this.sl.initScene(stateData, keywordData))
  }
}
</script>

<style>
#streamview {
  position: relative;
  float:left;
  -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
  filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) );
  width: 90%;
  /* height: 350px;
  overflow: auto; */
}
.streamview-text {
  font-family: "Times New Roman", Times, serif;
  font-weight: bold;
  font-size: px;
}
.streamview-tooltip {
  background-color: hsla(0,0%,100%,.9);
  padding: 10px;
  border-radius: 5px;
  font-size: 7px;
	width: 180px;
  height: 250px;
  position: absolute;
  z-index: 20;
}
.streamview-tooltip .date {
  /* font-weight: 900; */
  font-size: 10px;
  margin-bottom: 2px;
}
.streamview-tooltip .selected {
  /* font-weight: 900; */
  color: #E8175D;
}
</style>
