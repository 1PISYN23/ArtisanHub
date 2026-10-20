<template>
  <div class="coming-soon">
    <div class="coming-soon-icon">{{ icon }}</div>
    <h1>{{ title }}</h1>
    <p>{{ description }}</p>
    <div class="coming-soon-features">
      <div v-for="f in features" :key="f" class="coming-soon-feature">
        <span>◆</span><span>{{ f }}</span>
      </div>
    </div>
    <RouterLink to="/shops" class="btn">← К магазинам</RouterLink>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '🚧' },
  title: String,
  description: String,
  features: { type: Array, default: () => [] }
})
</script>