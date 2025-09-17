<script setup>
import { RouterLink, RouterView } from 'vue-router';
import Header from './components/Header.vue';

</script>

<template>
  <main class="max-w-7xl mx-auto">
    <Header></Header>
    <RouterView class="mt-14" />
  </main>
</template>