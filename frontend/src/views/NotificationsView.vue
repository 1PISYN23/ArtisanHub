<template>
  <ComingSoon icon="🔔" title="Уведомления"
    description="Новый заказ (продавцу), смена статуса (покупателю), новое сообщение в чате, товар из избранного скоро закончится."
    :features="[
      'In-app уведомления',
      'Email через Celery',
      'Единая модель с типом и payload',
      'Отметка «прочитано»'
    ]" />
</template>

<script setup>
import ComingSoon from '../components/ComingSoon.vue'
</script>