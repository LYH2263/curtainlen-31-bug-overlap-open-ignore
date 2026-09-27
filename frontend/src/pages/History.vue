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
<p class="hint">开放视图保留对开 / 重叠标记；成品宽与米数按整幅重算后的列表字段。</p>
</div></template>
