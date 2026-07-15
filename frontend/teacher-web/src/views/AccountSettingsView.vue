<script setup lang="ts">
import { ref } from 'vue'; import AppShell from '../components/AppShell.vue'
const compact=ref(localStorage.getItem('teacher_compact_mode')==='true'),reminders=ref(localStorage.getItem('teacher_class_reminders')!=='false'),saved=ref(false)
function save(){localStorage.setItem('teacher_compact_mode',String(compact.value));localStorage.setItem('teacher_class_reminders',String(reminders.value));saved.value=true;window.setTimeout(()=>saved.value=false,1800)}
</script>
<template><AppShell><div class="page-heading"><div><p class="eyebrow">账户</p><h1>账号设置</h1><p>调整当前设备上的工作台偏好。</p></div></div><section class="card settings-card"><div class="setting-row"><div><strong>紧凑内容布局</strong><p>在列表中显示更多教案和课堂信息。</p></div><label class="switch"><input v-model="compact" type="checkbox"><span></span></label></div><div class="setting-row"><div><strong>课堂开始提醒</strong><p>在工作台突出即将开始的课堂。</p></div><label class="switch"><input v-model="reminders" type="checkbox"><span></span></label></div><div class="button-row end"><span v-if="saved" class="success">设置已保存</span><button class="button primary" @click="save">保存设置</button></div></section></AppShell></template>
