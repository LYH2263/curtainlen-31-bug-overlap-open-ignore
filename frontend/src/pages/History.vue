<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/runs')).items })
</script>
<template><div class="page"><h1>记录</h1><ul><li v-for="r in items" :key="r.id">
  <router-link :to="`/bench?run=${r.id}`">#{{ r.id }}</router-link>
  {{ r.window_name }}（{{ r.result?.open_style === 'split' ? '对开' : '整幅' }}）
  重叠 {{ r.result?.overlap ?? 0 }} m · 成品宽 {{ r.result?.finished_width }} m / {{ r.result?.meters }}m
</li></ul>
<p class="hint">列表与详情均展示写入时固化的结果；事后修改默认重叠不影响已存编号。</p>
</div></template>
