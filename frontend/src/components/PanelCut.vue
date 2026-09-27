<script setup>
import { computed } from 'vue'
const props = defineProps({ panels: Number, cutHeight: Number, meters: Number, openStyle: { type: String, default: 'whole' } })
const shown = computed(() => Math.min(props.panels || 0, 12))
const leftCount = computed(() => Math.ceil(shown.value / 2))
</script>
<template>
  <div class="panel-cut">
    <template v-if="openStyle === 'split'">
      <div v-for="n in leftCount" :key="'l'+n" class="panel split-left" :style="{height: `${(cutHeight||1)*40}px`}"></div>
      <span class="seam" title="中缝重叠">中缝</span>
      <div v-for="n in shown - leftCount" :key="'r'+n" class="panel split-right" :style="{height: `${(cutHeight||1)*40}px`}"></div>
    </template>
    <template v-else>
      <div v-for="n in shown" :key="n" class="panel" :style="{height: `${(cutHeight||1)*40}px`}"></div>
    </template>
    <p>{{ panels }} 幅 × {{ cutHeight }} m = {{ meters }} m（{{ openStyle === 'split' ? '对开' : '整幅' }}）</p>
  </div>
</template>
