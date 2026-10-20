<template>
  <ComingSoon icon="🛒" title="Корзина"
    description="Товары из разных магазинов — в одном заказе. Один платёж, автоматическое разделение на под-заказы."
    :features="[
      'Позиции от нескольких продавцов сразу',
      'Группировка по магазинам',
      'Применение промокодов',
      'Автоматическое списание остатков при оформлении'
    ]" />
</template>

<script setup>
import ComingSoon from '../components/ComingSoon.vue'
</script>