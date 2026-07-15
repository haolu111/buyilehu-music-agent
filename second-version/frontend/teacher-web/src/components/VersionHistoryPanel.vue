<script setup lang="ts">
import type { PackageVersion } from '../types'

defineProps<{
  versions: PackageVersion[]
}>()
</script>

<template>
  <section class="card stack">
    <div class="section-header">
      <div>
        <h2>版本历史</h2>
        <p class="muted">每次保存都会生成一个新版本</p>
      </div>
    </div>
    <div v-if="versions.length === 0" class="muted">暂无版本</div>
    <div v-for="version in versions" :key="version.id" class="list-line">
      <div>
        <strong>v{{ version.versionNo }}</strong>
        <p class="muted">{{ version.remark || '版本记录' }}</p>
      </div>
      <span class="tag">{{ version.status }}</span>
    </div>
  </section>
</template>