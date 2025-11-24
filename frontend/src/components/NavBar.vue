<template>
  <nav class="navbar">
    <h1 class="title">Pi NVR Dashboard</h1>
    <ul class="menu">
      <li><router-link to="/">Cameras</router-link></li>
    </ul>
  </nav>
</template>

<style>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  background: #1a1a1a;
  color: white;
}
.title {
  font-size: 20px;
  font-weight: bold;
}
.menu {
  list-style: none;
  display: flex;
  gap: 20px;
}
.menu a {
  color: white;
  text-decoration: none;
  font-size: 16px;
}
.menu a:hover {
  color: #42b883;
}
</style>
