<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <router-link to="/" class="brand">Pi NVR</router-link>
      <ul class="menu">
        <li>
          <router-link to="/cameras" active-class="active">Cameras</router-link>
        </li>
      </ul>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  background-color: #0a1020;
  border-bottom: 1px solid var(--border);
}
.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.9rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.brand {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text);
  letter-spacing: 0.02em;
}
.brand:hover {
  color: var(--text);
}
.menu {
  list-style: none;
  display: flex;
  gap: 0.25rem;
  margin: 0;
  padding: 0;
}
.menu a {
  display: inline-block;
  color: var(--text-muted);
  padding: 0.45rem 0.85rem;
  border-radius: var(--radius-sm);
  font-weight: 500;
}
.menu a:hover {
  color: var(--text);
  background-color: var(--surface);
}
.menu a.active {
  color: var(--text);
  background-color: var(--accent-soft);
}
</style>
