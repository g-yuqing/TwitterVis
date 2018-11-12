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
    this.eventHub.$on('initStateView', dataset => this.sl.initScene(dataset))
    // this.eventHub.$on('updateStateView', data => this.sl.updateNode(data))
    this.eventHub.$on('showStateClusters', () => this.sl.showClusters())
    this.eventHub.$on('updateStateView', () => this.sl.updateStateView())
    this.eventHub.$on('resetOriginView', () => this.sl.resetOriginView())
  }
}
</script>

<style>
  #stateview {
    position: relative;
    float: left;
    -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
    filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) )
  }
</style>
