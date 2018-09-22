<template>
  <div id="tsnelayout"></div>
</template>

<script>
import Tsnelayout from '../scripts/tsnelayout'

export default {
  name: 'Tsnelayout',
  data() {
    return {
      tl: new Tsnelayout(),
    }
  },
  mounted() {
    this.eventHub.$on('initTsnelayout', dataset => this.tl.initScene(dataset))
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
  #tsnelayout {
    -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
    filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) )
  }
</style>
