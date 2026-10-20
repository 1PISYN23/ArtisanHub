<template>
  <RouterLink :to="`/shops/${shop.slug}`" class="shop-card">
    <img v-if="shop.logo" :src="shop.logo" :alt="shop.name" />
    <div v-else class="placeholder">{{ shop.name[0] }}</div>
    <div class="shop-card-body">
      <div class="shop-card-title">{{ shop.name }}</div>
      <div class="shop-card-desc">{{ shop.description || 'Без описания' }}</div>
      <div class="shop-card-meta">
        <span>⭐ {{ shop.rating_cached }}</span>
        <span>{{ shop.reviews_count_cached }} отзывов</span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
defineProps({ shop: { type: Object, required: true } })
</script>