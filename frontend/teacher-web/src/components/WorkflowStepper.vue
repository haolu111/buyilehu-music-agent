<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const workflowStages = [
  { id: 'upload-lesson', label: '上传教案' },
  { id: 'confirm-content', label: '确认内容' },
  { id: 'setup-classroom', label: '设置课堂' },
  { id: 'confirm-proposal', label: '确认方案' },
  { id: 'edit-package', label: '编辑互动包' },
  { id: 'publish-classroom', label: '发布课堂' },
] as const

const classroomControlStage = { id: 'classroom-control', label: '课堂控制' } as const

type WorkflowStage = typeof workflowStages[number]['id'] | typeof classroomControlStage.id
type WorkflowRoutes = Partial<Record<WorkflowStage, string>>

const props = defineProps<{
  currentStage: WorkflowStage
  routes?: WorkflowRoutes
  lessonPlanId?: number | string
  packageId?: number | string
  sessionId?: number | string
  showClassroomControl?: boolean
}>()

function defaultRoute(stage: WorkflowStage): string | undefined {
  if (stage === 'upload-lesson') return '/lesson-plans/upload'
  if (stage === 'confirm-content' && props.lessonPlanId) return `/lesson-plans/${props.lessonPlanId}/parse-result`
  if (stage === 'setup-classroom' && props.lessonPlanId) return `/packages/generate?lessonPlanId=${props.lessonPlanId}`
  if (stage === 'confirm-proposal' && props.packageId) return `/packages/${props.packageId}/proposal`
  if (stage === 'edit-package' && props.packageId) return `/packages/${props.packageId}/edit`
  if (stage === 'publish-classroom' && props.packageId) return `/packages/${props.packageId}/publish`
  if (stage === 'classroom-control' && props.sessionId) return `/classroom/${props.sessionId}/control`
  return undefined
}

const availableStages = computed(() => props.showClassroomControl ? [...workflowStages, classroomControlStage] : workflowStages)
const currentIndex = computed(() => availableStages.value.findIndex((stage) => stage.id === props.currentStage))
const steps = computed(() => availableStages.value.map((stage, index) => ({
  ...stage,
  state: index < currentIndex.value ? 'completed' : index === currentIndex.value ? 'current' : 'upcoming',
  route: props.routes?.[stage.id] || defaultRoute(stage.id),
})))
</script>

<template>
  <nav class="workflow-stepper" aria-label="备课与课堂流程">
    <ol>
      <li
        v-for="(stage, index) in steps"
        :key="stage.id"
        :data-stage="stage.id"
        :data-state="stage.state"
        :aria-current="stage.state === 'current' ? 'step' : undefined"
      >
        <RouterLink v-if="stage.state === 'completed' && stage.route" :to="stage.route">
          <span class="workflow-stepper-number">{{ index + 1 }}</span>
          {{ stage.label }}
        </RouterLink>
        <span v-else :aria-disabled="stage.state === 'upcoming' ? 'true' : undefined">
          <span class="workflow-stepper-number">{{ index + 1 }}</span>
          {{ stage.label }}
        </span>
      </li>
    </ol>
  </nav>
</template>
