<template>
  <form class="form" @submit.prevent="onSubmit">
    <label class="field">
      <span>Username</span>
      <input v-model="form.username" type="text" autocomplete="off" required autofocus />
    </label>

    <label class="field">
      <span>Password</span>
      <input
        v-model="form.password"
        type="password"
        autocomplete="new-password"
        required
        minlength="4"
      />
      <small class="hint">At least 4 characters.</small>
    </label>

    <label class="checkbox-field">
      <input v-model="form.is_admin" type="checkbox" />
      <span>Admin (can manage users)</span>
    </label>

    <div v-if="error" class="error">{{ error }}</div>

    <div class="actions">
      <button type="button" class="btn-ghost" @click="$emit('cancel')">Cancel</button>
      <button type="submit" class="btn-primary" :disabled="saving">
        {{ saving ? "Saving…" : "Add user" }}
      </button>
    </div>
  </form>
</template>

<script>
export default {
  props: {
    onSave: { type: Function, required: true },
  },
  emits: ["cancel"],
  data() {
    return {
      form: { username: "", password: "", is_admin: false },
      saving: false,
      error: "",
    };
  },
  methods: {
    async onSubmit() {
      this.saving = true;
      this.error = "";
      try {
        await this.onSave({ ...this.form });
      } catch (err) {
        this.error = err?.response?.data?.detail || err?.message || "Save failed";
      } finally {
        this.saving = false;
      }
    },
  },
};
</script>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.field > span {
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
}
.hint {
  color: var(--text-dim);
  font-size: 0.8rem;
}
.checkbox-field {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text);
  font-size: 0.9rem;
}
.checkbox-field input {
  width: auto;
}
.error {
  color: var(--danger);
  background: rgba(248, 113, 113, 0.08);
  border: 1px solid rgba(248, 113, 113, 0.25);
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.25rem;
}
</style>
