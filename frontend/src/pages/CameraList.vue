<template>
  <section class="page">
    <header class="page-header">
      <h2>Cameras</h2>
      <p class="subtitle">Manage and control your camera streams.</p>
    </header>

    <div v-if="loading" class="empty">Loading cameras…</div>

    <div v-else-if="!cameras.length" class="empty card">
      <h3>No cameras yet</h3>
      <p>Cameras you add will appear here.</p>
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
      </article>
    </div>
  </section>
</template>

<script>
import cameraAPI from "../api/cameras";
import streamAPI from "../api/streams";

export default {
  data() {
    return {
      cameras: [],
      loading: true,
    };
  },
  mounted() {
    this.loadCameras();
  },
  methods: {
    async loadCameras() {
      this.loading = true;
      try {
        const res = await cameraAPI.list();
        this.cameras = res.data;
      } finally {
        this.loading = false;
      }
    },
    async startStream(id) {
      await streamAPI.start(id);
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
  },
};
</script>

<style scoped>
.page-header {
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
  margin-top: auto;
}
</style>
