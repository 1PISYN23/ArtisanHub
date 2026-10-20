<template>
  <footer class="footer">
    <div class="footer-links">
      <RouterLink to="/catalog">Каталог</RouterLink>
      <RouterLink to="/shops">Магазины</RouterLink>
      <a href="#" @click.prevent>О платформе</a>
      <a href="#" @click.prevent>Помощь</a>
    </div>
    <div>© {{ year }} ArtisanHub — маркетплейс ручной работы</div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>