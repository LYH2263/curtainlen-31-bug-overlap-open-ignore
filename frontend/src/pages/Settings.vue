<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const overlap = ref('')
const msg = ref('')
onMounted(async () => {
  s.value = await getJSON('/api/settings')
  overlap.value = s.value.default_overlap ?? '0.10'
})
async function save() {
  msg.value = ''
  const v = parseFloat(overlap.value)
  if (!Number.isFinite(v) || v < 0) { msg.value = '默认重叠不能小于 0'; return }
  s.value = await putJSON('/api/settings', { key: 'default_overlap', value: String(v) })
  msg.value = '已保存；仅影响新测算，旧编号保持原值。'
}
</script>
<template><div class="page"><h1>设置</h1>
<p>默认褶倍 {{ s.default_fullness }}</p>
<div class="fab">默认中缝重叠 <input type="number" min="0" step="0.01" v-model="overlap" style="width:5rem" /> m
  <button @click="save">保存默认重叠</button></div>
<p v-if="msg" :class="{ bad: msg.includes('不能') }">{{ msg }}</p>
</div></template>
