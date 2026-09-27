<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
import PanelCut from '../components/PanelCut.vue'
const route = useRoute()
const windows = ref([]); const fabrics = ref([])
const wid = ref(1); const fid = ref(1)
const openStyle = ref('whole')
const overlapStr = ref('')
const defaultOverlap = ref(0)
const out = ref(null)
const err = ref('')
const savedId = ref(null)
const loadedRun = ref(null)

function overlapValue() {
  const v = parseFloat(overlapStr.value)
  return Number.isFinite(v) ? v : null
}

async function go(save) {
  err.value = ''; savedId.value = null; loadedRun.value = null
  let overlap = null
  if (openStyle.value === 'split') {
    overlap = overlapValue()
    if (overlap === null || overlap < 0) {
      err.value = '中缝重叠不能小于 0'
      return
    }
  }
  try {
    if (save) {
      out.value = await postJSON('/api/estimate', {
        window_id: wid.value, fabric_id: fid.value, save: true,
        open_style: openStyle.value, overlap,
      })
    } else {
      const q = new URLSearchParams({ window_id: String(wid.value), fabric_id: String(fid.value), open_style: openStyle.value })
      if (openStyle.value === 'split') q.set('overlap', String(overlap))
      out.value = await getJSON(`/api/estimate?${q}`)
    }
    if (out.value.run_id) savedId.value = out.value.run_id
  } catch (e) {
    err.value = '测算失败：' + e.message.replace(/^Error: /, '')
  }
}

onMounted(async () => {
  windows.value = (await getJSON('/api/windows')).items.filter(x => x.data_quality === 'clean')
  fabrics.value = (await getJSON('/api/fabrics')).items.filter(x => x.data_quality === 'clean')
  const s = await getJSON('/api/settings')
  defaultOverlap.value = parseFloat(s.default_overlap || '0') || 0
  if (windows.value.length) wid.value = windows.value[0].id
  if (fabrics.value.length) fid.value = fabrics.value[0].id
  overlapStr.value = String(defaultOverlap.value)
  const runNo = route.query.run
  if (runNo) {
    // 按编号打开：开合方式/重叠/成品宽/米数全部读当初固化的结果，不用新默认值改写
    const r = await getJSON(`/api/runs/${runNo}`)
    wid.value = r.window_id
    fid.value = r.fabric_id
    const res = r.result || {}
    openStyle.value = res.open_style || 'whole'
    overlapStr.value = String(res.overlap ?? defaultOverlap.value)
    out.value = res
    loadedRun.value = Number(runNo)
  }
})
</script>
<template><div class="page"><h1>算料</h1>
<select v-model.number="wid"><option v-for="x in windows" :key="x.id" :value="x.id">{{ x.name }}</option></select>
<select v-model.number="fid"><option v-for="x in fabrics" :key="x.id" :value="x.id">{{ x.name }}</option></select>
<div class="fab">
  <label><input type="radio" value="whole" v-model="openStyle" /> 整幅</label>
  <label><input type="radio" value="split" v-model="openStyle" /> 对开</label>
  <span v-if="openStyle==='split'">
    中缝重叠 <input type="number" min="0" step="0.01" v-model="overlapStr" style="width:5rem" /> m
  </span>
</div>
<p v-if="out" class="fab">成品宽 {{ out.finished_width }} m（{{ out.open_style === 'split' ? '对开：窗宽×褶倍 + 中缝重叠' : '整幅：窗宽×褶倍' }}）</p>
<p v-if="err" class="bad">{{ err }}</p>
<button @click="go(false)">试算</button><button @click="go(true)">保存</button>
<p v-if="loadedRun" class="fab">已按编号 #{{ loadedRun }} 打开（当初开合方式与结果已固化）</p>
<p v-else-if="savedId" class="fab">已保存为编号 <router-link :to="`/bench?run=${savedId}`">#{{ savedId }}</router-link></p>
<PanelCut v-if="out" :panels="out.panels" :cut-height="out.cut_height" :meters="out.meters" :open-style="out.open_style" />
</div></template>
