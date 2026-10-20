<template>
  <ComingSoon icon="📦" title="Мои заказы"
    description="Каждый заказ разбивается на под-заказы по магазинам. Каждый под-заказ со своим статусом: pending → confirmed → shipped → delivered."
    :features="[
      'История статусов под-заказов',
      'Один общий статус заказа',
      'Отмена до определённого статуса',
      'Отзыв только после доставки'
    ]" />
</template>

<script setup>
import ComingSoon from '../components/ComingSoon.vue'
</script>