<template>
  <ComingSoon icon="♥" title="Избранное"
    description="Избранные товары и магазины. Уведомим, если товар подешевел или осталось мало единиц."
    :features="[
      'Избранные товары и магазины отдельно',
      'Уведомление о снижении цены',
      'Уведомление о скором окончании остатка',
      'Быстрое добавление в корзину'
    ]" />
</template>

<script setup>
import ComingSoon from '../components/ComingSoon.vue'
</script>