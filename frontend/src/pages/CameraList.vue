<template>
  <section class="page">
    <header class="page-header">
      <div>
        <h2>Cameras</h2>
        <p class="subtitle">Manage and control your camera streams.</p>
      </div>
      <button class="btn-primary" @click="openCreate">+ Add Camera</button>
    </header>

    <div v-if="loading" class="empty">Loading cameras…</div>

    <div v-else-if="loadError" class="empty card danger-card">
      <h3>Couldn't reach the backend</h3>
      <p>{{ loadError }}</p>
      <button @click="loadCameras">Retry</button>
    </div>

    <div v-else-if="!cameras.length" class="empty card">
      <h3>No cameras yet</h3>
      <p>Click <strong>+ Add Camera</strong> to add your first one.</p>
    </div>

    <div v-else class="camera-grid">
      <article v-for="cam in cameras" :key="cam.id" class="camera-card card">
        <div class="card-head">
          <h3>{{ cam.name }}</h3>
          <span class="badge" :class="statusClass(cam.status)">
            {{ cam.status || "unknown" }}
          </span>
        </div>

        <p class="rtsp" :title="cam.rtsp_url">{{ cam.rtsp_url }}</p>

        <div class="buttons">
          <button class="btn-primary" @click="startStream(cam.id)">Start</button>
          <button @click="stopStream(cam.id)">Stop</button>
          <router-link :to="`/live/${cam.id}`" class="btn btn-ghost">
            Live View
          </router-link>
        </div>

        <div class="row-actions">
          <button class="btn-ghost small" @click="openEdit(cam)">Edit</button>
          <button class="btn-danger small" @click="deleteCamera(cam)">
            Delete
          </button>
        </div>
      </article>
    </div>

    <Modal :open="formOpen" :title="editing ? 'Edit camera' : 'Add camera'" @close="closeForm">
      <CameraForm
        :initial="editing || { name: '', rtsp_url: '' }"
        :submit-label="editing ? 'Save changes' : 'Add camera'"
        :on-save="onFormSubmit"
        @cancel="closeForm"
      />
    </Modal>
  </section>
</template>

<script>
import cameraAPI from "../api/cameras";
import streamAPI from "../api/streams";
import CameraForm from "../components/CameraForm.vue";
import Modal from "../components/Modal.vue";

export default {
  components: { CameraForm, Modal },
  data() {
    return {
      cameras: [],
      loading: true,
      loadError: "",
      formOpen: false,
      editing: null,
    };
  },
  mounted() {
    this.loadCameras();
  },
  methods: {
    async loadCameras() {
      this.loading = true;
      this.loadError = "";
      try {
        const res = await cameraAPI.list();
        this.cameras = res.data;
      } catch (err) {
        this.loadError =
          err?.response?.data?.detail || err?.message || "Network error";
      } finally {
        this.loading = false;
      }
    },
    async startStream(id) {
      try {
        await streamAPI.start(id);
      } catch (err) {
        const msg = err?.response?.data?.detail || "Couldn't start stream";
        alert(msg);
      }
      this.loadCameras();
    },
    async stopStream(id) {
      await streamAPI.stop(id);
      this.loadCameras();
    },
    statusClass(status) {
      switch ((status || "").toLowerCase()) {
        case "streaming":
          return "success";
        case "offline":
        case "stopped":
          return "muted";
        case "error":
          return "danger";
        default:
          return "warning";
      }
    },
    openCreate() {
      this.editing = null;
      this.formOpen = true;
    },
    openEdit(camera) {
      this.editing = { ...camera };
      this.formOpen = true;
    },
    closeForm() {
      this.formOpen = false;
      this.editing = null;
    },
    async onFormSubmit(values) {
      if (this.editing) {
        await cameraAPI.update(this.editing.id, values);
      } else {
        await cameraAPI.create(values);
      }
      this.closeForm();
      this.loadCameras();
    },
    async deleteCamera(camera) {
      const ok = window.confirm(
        `Delete "${camera.name}"? This stops the stream and removes its files.`
      );
      if (!ok) return;
      try {
        await cameraAPI.remove(camera.id);
      } catch (err) {
        alert(err?.response?.data?.detail || "Delete failed");
      }
      this.loadCameras();
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
.camera-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
.camera-card {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.card-head h3 {
  margin: 0;
}
.rtsp {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-dim);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.row-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border);
}
.small {
  padding: 0.35rem 0.7rem;
  font-size: 0.85rem;
}
</style>
