<template>
  <div id="keywordview">
    <!-- <div id="keywordtag">
      <el-row>
        <el-checkbox-group v-model="checkboxGroup" size="mini">
          <el-checkbox-button v-for="keyword in keywords"
            :label="keyword"
            :key="keyword">{{keyword}}
          </el-checkbox-button>
        </el-checkbox-group>
      </el-row> -->
    </div>
  </div>
</template>

<script>
import Keywordlayout from '../scripts/keywordlayout'

export default {
  name: 'KeywordView',
  data() {
    return {
      kl: new Keywordlayout(),
    }
  },
  mounted() {
    this.eventHub.$on('initKeywordView', data => this.kl.initScene(data))
  }
}
</script>

<style>
#keywordview {
  position: relative;
  float: left;
  -webkit-filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.3) );
  filter: drop-shadow( 0px 3px 3px rgba(0,0,0,.25) )
}
</style>
