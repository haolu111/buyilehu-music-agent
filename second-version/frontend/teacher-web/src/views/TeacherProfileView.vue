<script setup lang="ts">
import AppShell from '../components/AppShell.vue'; import { useAuthStore } from '../stores/authStore'
const auth=useAuthStore()
</script>
<template><AppShell><div class="page-heading"><div><p class="eyebrow">账户</p><h1>个人信息</h1><p>查看当前登录的教师身份信息。</p></div></div><section class="card account-card"><div class="profile-hero"><span>{{ (auth.user?.displayName||auth.user?.realName||'教').slice(0,1) }}</span><div><h2>{{ auth.user?.displayName||auth.user?.realName||'音乐教师' }}</h2><p>{{ auth.user?.username }}</p></div></div><dl><div><dt>教师姓名</dt><dd>{{ auth.user?.displayName||auth.user?.realName||'未设置' }}</dd></div><div><dt>登录账号</dt><dd>{{ auth.user?.username||'-' }}</dd></div><div><dt>账户角色</dt><dd>音乐教师</dd></div><div><dt>账户状态</dt><dd><span class="status-pill active">正常使用</span></dd></div></dl><p class="account-note">姓名、学校等资料由系统管理员统一维护。</p></section></AppShell></template>
