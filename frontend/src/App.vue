<template>
  <NavBar />
  <main class="container">
    <router-view />
  </main>
</template>

<script>
import NavBar from "./components/NavBar.vue";
export default {
  components: { NavBar },
};
</script>
