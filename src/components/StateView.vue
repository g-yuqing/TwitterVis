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
  }
}
</script>

<style>
  .dot {
    /* stroke: #000; */
  }
  .axis--grid .domain {
    fill: #ddd;
    stroke: none;
  }
  .axis--x .domain,
  .axis--grid .tick line {
    stroke: #fff;
  }
  .axis--grid .tick--minor line {
    stroke-opacity: 0.5;
  }
  .brush .selection {
    fill: steelblue;
  }
  #stateview {
    position: relative;
    float: left;
    -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
    filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) )
  }
  .hull {
    opacity: 0.2;
    /* stroke-opacity: 0.3; */
    stroke-width: 32px;
    stroke-linejoin: round;
  }
  text.mono {
    font-family: Consolas, courier;
    fill: #000;
  }
</style>
