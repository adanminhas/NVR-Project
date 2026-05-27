<template>
  <section class="page">
    <header class="page-header">
      <div>
        <h2>Users</h2>
        <p class="subtitle">Add or remove people who can sign in.</p>
      </div>
      <button class="btn-primary" @click="formOpen = true">+ Add User</button>
    </header>

    <div v-if="loading" class="empty">Loading users…</div>

    <div v-else-if="loadError" class="empty card danger-card">
      <h3>Couldn't load users</h3>
      <p>{{ loadError }}</p>
      <button @click="loadUsers">Retry</button>
    </div>

    <ul v-else class="user-list">
      <li v-for="user in users" :key="user.id" class="user-row card">
        <div class="user-info">
          <strong>{{ user.username }}</strong>
          <span class="badge" :class="user.is_admin ? 'success' : 'muted'">
            {{ user.is_admin ? "admin" : "user" }}
          </span>
          <span v-if="isSelf(user)" class="badge muted">you</span>
        </div>
        <button
          class="btn-danger small"
          :disabled="isSelf(user)"
          :title="isSelf(user) ? 'You cannot delete yourself' : ''"
          @click="deleteUser(user)"
        >
          Delete
        </button>
      </li>
    </ul>

    <Modal :open="formOpen" title="Add user" @close="formOpen = false">
      <UserForm :on-save="onCreate" @cancel="formOpen = false" />
    </Modal>
  </section>
</template>

<script>
import { authState } from "../api/auth";
import userAPI from "../api/users";
import Modal from "../components/Modal.vue";
import UserForm from "../components/UserForm.vue";

export default {
  components: { Modal, UserForm },
  data() {
    return {
      users: [],
      loading: true,
      loadError: "",
      formOpen: false,
    };
  },
  mounted() {
    this.loadUsers();
  },
  methods: {
    async loadUsers() {
      this.loading = true;
      this.loadError = "";
      try {
        const res = await userAPI.list();
        this.users = res.data;
      } catch (err) {
        this.loadError = err?.response?.data?.detail || err?.message || "Network error";
      } finally {
        this.loading = false;
      }
    },
    isSelf(user) {
      return authState.user && user.id === authState.user.id;
    },
    async onCreate(values) {
      await userAPI.create(values);
      this.formOpen = false;
      this.loadUsers();
    },
    async deleteUser(user) {
      if (!window.confirm(`Delete user "${user.username}"?`)) return;
      try {
        await userAPI.remove(user.id);
      } catch (err) {
        alert(err?.response?.data?.detail || "Delete failed");
      }
      this.loadUsers();
    },
  },
};
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.page-header h2 {
  margin: 0 0 0.25rem;
}
.subtitle {
  color: var(--text-muted);
  margin: 0;
}
.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
}
.danger-card {
  border-color: rgba(248, 113, 113, 0.35);
}
.user-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.user-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.85rem 1rem;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.small {
  padding: 0.35rem 0.7rem;
  font-size: 0.85rem;
}

@media (max-width: 640px) {
  .user-row {
    flex-direction: column;
    align-items: stretch;
    gap: 0.6rem;
  }
  .user-info {
    flex-wrap: wrap;
  }
  .small {
    padding: 0.5rem 0.8rem;
    font-size: 0.9rem;
    align-self: flex-end;
  }
}
</style>
