<template>
  <div class="login-wrapper">
    <div class="login-card card">
      <h2>Sign in</h2>
      <p class="subtitle">Pi NVR</p>

      <form @submit.prevent="onSubmit" class="form">
        <label class="field">
          <span>Username</span>
          <input
            v-model="form.username"
            type="text"
            autocomplete="username"
            required
            autofocus
          />
        </label>
        <label class="field">
          <span>Password</span>
          <input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            required
          />
        </label>

        <div v-if="error" class="error">{{ error }}</div>

        <button type="submit" class="btn-primary" :disabled="submitting">
          {{ submitting ? "Signing in…" : "Sign in" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { login } from "../api/auth";

export default {
  data() {
    return {
      form: { username: "", password: "" },
      submitting: false,
      error: "",
    };
  },
  methods: {
    async onSubmit() {
      this.submitting = true;
      this.error = "";
      try {
        await login(this.form.username, this.form.password);
        const redirect = this.$route.query.redirect || "/cameras";
        this.$router.replace(redirect);
      } catch (err) {
        this.error =
          err?.response?.data?.detail || err?.message || "Sign-in failed";
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>

<style scoped>
.login-wrapper {
  min-height: calc(100vh - 4rem);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.login-card {
  width: 100%;
  max-width: 380px;
}
.login-card h2 {
  margin: 0 0 0.25rem;
}
.subtitle {
  color: var(--text-muted);
  margin: 0 0 1.25rem;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.field > span {
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
}
.error {
  color: var(--danger);
  background: rgba(248, 113, 113, 0.08);
  border: 1px solid rgba(248, 113, 113, 0.25);
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}
</style>
