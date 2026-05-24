<template>
  <form @submit.prevent="onSubmit" class="form">
    <label class="field">
      <span>Name</span>
      <input
        v-model="form.name"
        type="text"
        placeholder="Front door"
        required
        autofocus
      />
    </label>

    <label class="field">
      <span>RTSP URL</span>
      <input
        v-model="form.rtsp_url"
        type="text"
        placeholder="rtsp://user:pass@host:554/stream"
        required
      />
      <small class="hint">
        Example: <code>rtsp://192.168.1.50:554/Streaming/Channels/101</code>
      </small>
    </label>

    <div v-if="error" class="error">{{ error }}</div>

    <div class="actions">
      <button type="button" class="btn-ghost" @click="$emit('cancel')">
        Cancel
      </button>
      <button type="submit" class="btn-primary" :disabled="saving">
        {{ saving ? "Saving…" : submitLabel }}
      </button>
    </div>
  </form>
</template>

<script>
export default {
  props: {
    initial: { type: Object, default: () => ({ name: "", rtsp_url: "" }) },
    submitLabel: { type: String, default: "Save" },
    onSave: { type: Function, required: true },
  },
  emits: ["cancel"],
  data() {
    return {
      form: {
        name: this.initial.name || "",
        rtsp_url: this.initial.rtsp_url || "",
      },
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
.hint code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.78rem;
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
