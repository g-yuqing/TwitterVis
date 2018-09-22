<template>
  <div id="forcelayout">
    <div id="main-container"></div>
  </div>
</template>

<script>
import Forcelayout from '../scripts/forcelayout'

export default {
  name: 'Forcelayout',
  data: () => ({
    fl: new Forcelayout(),
  }),
  mounted() {
    this.eventHub.$on('initForcelayoutScene', data => this.fl.initScene(data))
  },
  // watch: {
  //   fl: {
  //     handler: function() {
  //       this.eventHub.$emit('getPosData', this.fl.posData)
  //     },
  //     deep: true
  //   }
  // },
}
</script>

<style>
#forcelayout {
  float: left;
}
.nodes circle {

}
</style>
