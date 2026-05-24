<template>
  <Teleport to="body">
    <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal-card card" role="dialog" aria-modal="true">
        <header class="modal-header">
          <h3>{{ title }}</h3>
          <button class="btn-ghost icon" @click="$emit('close')" aria-label="Close">
            ×
          </button>
        </header>
        <div class="modal-body">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
export default {
  props: {
    open: { type: Boolean, required: true },
    title: { type: String, default: "" },
  },
  emits: ["close"],
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(5, 9, 17, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 50;
  backdrop-filter: blur(2px);
}
.modal-card {
  width: 100%;
  max-width: 460px;
  padding: 0;
  overflow: hidden;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border);
}
.modal-header h3 {
  margin: 0;
}
.icon {
  width: 2rem;
  height: 2rem;
  padding: 0;
  font-size: 1.2rem;
  line-height: 1;
}
.modal-body {
  padding: 1.25rem;
}
</style>
