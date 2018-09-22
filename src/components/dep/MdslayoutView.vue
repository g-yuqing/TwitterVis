<template>
  <div id="mdslayout"></div>
</template>

<script>
import Mdslayout from '../scripts/mdslayout'

export default {
  name: 'Mdslayout',
  data: () => ({
    ml: new Mdslayout(),
  }),
  mounted() {
    this.eventHub.$on('initMdslayoutScene', (dataset, tags) => this.ml.initScene(dataset, tags))
    this.eventHub.$on('updateMdslayoutScene', tags => this.ml.updateScene(tags))
  }
}
</script>

<style>
  .dot {
    /* stroke: #000; */
  }
 .axis path,
 .axis line{
   fill: none;
   stroke-width: 1px;
   stroke: #777;
 }
</style>
