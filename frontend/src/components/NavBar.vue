<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <router-link to="/" class="brand" @click="menuOpen = false">Pi NVR</router-link>

      <button
        v-if="authState.user"
        class="hamburger btn-ghost"
        aria-label="Toggle menu"
        :aria-expanded="menuOpen"
        @click="menuOpen = !menuOpen"
      >
        <span v-if="menuOpen">✕</span>
        <span v-else>☰</span>
      </button>

      <div v-if="authState.user" class="menu-wrap" :class="{ open: menuOpen }">
        <ul class="menu" @click="menuOpen = false">
          <li>
            <router-link to="/cameras" active-class="active">Cameras</router-link>
          </li>
          <li>
            <router-link to="/recordings" active-class="active">Recordings</router-link>
          </li>
          <li v-if="authState.user.is_admin">
            <router-link to="/users" active-class="active">Users</router-link>
          </li>
        </ul>
        <div class="account">
          <span class="user">{{ authState.user.username }}</span>
          <button class="btn-ghost small" @click="onLogout">Logout</button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { authState, logout } from "../api/auth";

export default {
  data() {
    return { authState, menuOpen: false };
  },
  watch: {
    $route() {
      this.menuOpen = false;
    },
  },
  methods: {
    onLogout() {
      logout();
      this.menuOpen = false;
      this.$router.replace({ name: "login" });
    },
  },
};
</script>

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
  gap: 1rem;
  flex-wrap: wrap;
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
.menu-wrap {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
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
.account {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.user {
  color: var(--text-muted);
  font-size: 0.9rem;
}
.small {
  padding: 0.35rem 0.7rem;
  font-size: 0.85rem;
}
.hamburger {
  display: none;
  width: 2.5rem;
  height: 2.5rem;
  padding: 0;
  font-size: 1.2rem;
  line-height: 1;
}

@media (max-width: 700px) {
  .navbar-inner {
    padding: 0.75rem 1rem;
  }
  .hamburger {
    display: inline-flex;
  }
  .menu-wrap {
    display: none;
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
    width: 100%;
    margin-left: 0;
    margin-top: 0.75rem;
    border-top: 1px solid var(--border);
    padding-top: 0.75rem;
  }
  .menu-wrap.open {
    display: flex;
  }
  .menu {
    flex-direction: column;
    gap: 0.25rem;
  }
  .menu a {
    padding: 0.7rem 0.85rem;
  }
  .account {
    justify-content: space-between;
  }
}
</style>
