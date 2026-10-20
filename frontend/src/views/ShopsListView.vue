<template>
  <div>
    <header class="page-header">
      <div>
        <h1>Магазины</h1>
        <p class="muted">Всего: {{ count }}</p>
      </div>
      <div class="toolbar">
        <input v-model="search" @input="onSearch" placeholder="🔍 Поиск по названию" class="toolbar-input" />
        <select v-model="ordering" @change="reload()" class="toolbar-select">
          <option value="name">По названию ↑</option>
          <option value="-name">По названию ↓</option>
          <option value="-created_at">Новые</option>
          <option value="-rating_cached">По рейтингу</option>
          <option value="-reviews_count_cached">По отзывам</option>
        </select>
      </div>
    </header>

    <div v-if="loading" class="grid">
      <SkeletonCard v-for="i in 8" :key="i" />
    </div>
    <div v-else-if="!shops.length" class="empty-state">
      <div class="empty-icon">🏪</div>
      <h3>Магазинов пока нет</h3>
      <p class="muted">{{ search ? 'По запросу ничего не найдено' : 'Станьте первым продавцом!' }}</p>
      <RouterLink v-if="!search && auth.isAuthenticated" to="/my-shop" class="btn">Создать магазин</RouterLink>
      <RouterLink v-if="!search && !auth.isAuthenticated" to="/register" class="btn">Зарегистрироваться</RouterLink>
    </div>
    <div v-else class="grid">
      <ShopCard v-for="shop in shops" :key="shop.id" :shop="shop" />
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button class="btn btn-secondary" :disabled="!prev" @click="go(page - 1)">←</button>
      <span class="page-info">Стр. {{ page }} из {{ totalPages }}</span>
      <button class="btn btn-secondary" :disabled="!next" @click="go(page + 1)">→</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ShopCard from '../components/ShopCard.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import { shopsApi } from '../api/shops'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const shops = ref([])
const loading = ref(false)
const search = ref('')
const ordering = ref('name')
const page = ref(1)
const next = ref(null)
const prev = ref(null)
const count = ref(0)
const totalPages = computed(() => Math.ceil(count.value / 20) || 1)

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, ordering: ordering.value }
    if (search.value) params.search = search.value
    const { data } = await shopsApi.list(params)
    shops.value = data.results
    next.value = data.next
    prev.value = data.previous
    count.value = data.count
  } catch (e) {
    console.error(e)
    shops.value = []
  } finally { loading.value = false }
}
function go(p) { page.value = p; load() }
function reload() { page.value = 1; load() }
let timer = null
function onSearch() {
  clearTimeout(timer)
  timer = setTimeout(() => { page.value = 1; load() }, 350)
}
onMounted(load)
</script>