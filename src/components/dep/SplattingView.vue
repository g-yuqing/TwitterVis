<template>
  <div id="splatting">
  </div>
</template>

<script>
import Splatting from '../scripts/splatting'

export default {
  name: 'Splatting',
  data: () => ({
    sp: new Splatting(),
  }),
  mounted() {
    this.eventHub.$on('initSplattingScene', (contours, words) => this.sp.initScene(contours, words))
  },
}
</script>

<style>
#splatting {
  float: left;
}
</style>
