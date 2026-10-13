<template>
  <Navbar v-if="!isAuthPage" />
  <RouterView />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'

const route = useRoute()
const isAuthPage = computed(() => route.meta.layout === 'auth')
</script>