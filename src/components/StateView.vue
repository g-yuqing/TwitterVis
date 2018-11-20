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
    this.eventHub.$on('updateStateView', () => this.sl.updateStateView())
    this.eventHub.$on('resetOriginView', () => this.sl.resetOriginView())
    this.eventHub.$on('showGroups', () => this.sl.showGroups())
    this.eventHub.$on('hideGroups', () => this.sl.hideGroups())
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
