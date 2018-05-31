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
    this.eventHub.$on('initSplattingScene', year => this.sp.initScene(year))
  },
}
</script>

<style>
#splatting {
  float: left;
}
</style>
