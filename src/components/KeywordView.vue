<template>
  <div id="keywordview">
    <div id="keywordtag">
      <el-row>
        <el-checkbox-group v-model="checkboxGroup" size="mini">
          <el-checkbox-button v-for="keyword in keywords"
            :label="keyword"
            :key="keyword">{{keyword}}
          </el-checkbox-button>
        </el-checkbox-group>
      </el-row>
    </div>
  </div>
</template>

<script>
import Keywordlayout from '../scripts/keywordlayout'

export default {
  name: 'KeywordView',
  data() {
    return {
      keywords
      kl: new Keywordlayout(),
    }
  },
  mounted() {
    this.eventHub.$on('initKeywordView', () => this.kl.initScene())
  }
}
</script>

<style>
</style>
