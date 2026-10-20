<template>
  <ComingSoon icon="💬" title="Чат с продавцом"
    description="Прямой real-time диалог по заказу или товару. Django Channels + WebSocket, история через REST."
    :features="[
      'WebSocket в реальном времени',
      'Индикатор «печатает»',
      'Статусы «прочитано/не прочитано»',
      'Уведомления о новых сообщениях'
    ]" />
</template>

<script setup>
import ComingSoon from '../components/ComingSoon.vue'
</script>