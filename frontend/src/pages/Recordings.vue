<template>
  <section class="page">
    <header class="page-header">
      <div>
        <h2>Recordings</h2>
        <p class="subtitle">Browse and play back recorded footage.</p>
      </div>
    </header>

    <div class="filters card">
      <label class="field">
        <span>Camera</span>
        <select v-model="filters.cameraId" @change="loadRecordings">
          <option :value="''">All cameras</option>
          <option v-for="cam in cameras" :key="cam.id" :value="cam.id">
            {{ cam.name }}
          </option>
        </select>
      </label>
      <label class="field">
        <span>From</span>
        <input v-model="filters.from" type="date" @change="loadRecordings" />
      </label>
      <label class="field">
        <span>To</span>
        <input v-model="filters.to" type="date" @change="loadRecordings" />
      </label>
      <button class="btn-ghost reset" @click="resetFilters">Reset</button>
    </div>

    <div v-if="loading" class="empty">Loading…</div>

    <div v-else-if="loadError" class="empty card danger-card">
      <h3>Couldn't load recordings</h3>
      <p>{{ loadError }}</p>
      <button @click="loadRecordings">Retry</button>
    </div>

    <div v-else-if="!recordings.length" class="empty card">
      <h3>No recordings found</h3>
      <p>Enable <strong>Record</strong> on a camera to start capturing footage.</p>
    </div>

    <ul v-else class="recording-list">
      <li v-for="rec in recordings" :key="rec.id" class="recording-row card">
        <div class="row-head" @click="toggleExpanded(rec.id)">
          <div>
            <div class="row-title">
              <strong>{{ cameraName(rec.camera_id) }}</strong>
              <span class="muted">·</span>
              <time>{{ formatDateTime(rec.started_at) }}</time>
            </div>
            <div class="row-meta">
              <span>{{ formatDuration(rec.duration_seconds) }}</span>
              <span class="muted">·</span>
              <span>{{ formatSize(rec.size_bytes) }}</span>
            </div>
          </div>
          <div class="row-actions" @click.stop>
            <a class="btn btn-ghost small" :href="downloadUrl(rec.id)" download> Download </a>
            <button class="btn-danger small" @click="deleteRecording(rec)">Delete</button>
          </div>
        </div>

        <div v-if="expanded === rec.id" class="player">
          <video :src="downloadUrl(rec.id)" controls playsinline></video>
        </div>
      </li>
    </ul>
  </section>
</template>

<script>
import cameraAPI from "../api/cameras";
import recordingAPI from "../api/recordings";

export default {
  data() {
    return {
      cameras: [],
      recordings: [],
      loading: true,
      loadError: "",
      expanded: null,
      filters: {
        cameraId: "",
        from: "",
        to: "",
      },
    };
  },
  async mounted() {
    await this.loadCameras();
    await this.loadRecordings();
  },
  methods: {
    async loadCameras() {
      try {
        const res = await cameraAPI.list();
        this.cameras = res.data;
      } catch {
        this.cameras = [];
      }
    },
    async loadRecordings() {
      this.loading = true;
      this.loadError = "";
      const params = {};
      if (this.filters.cameraId !== "") params.camera_id = this.filters.cameraId;
      if (this.filters.from) params.start_from = `${this.filters.from}T00:00:00`;
      if (this.filters.to) params.start_to = `${this.filters.to}T23:59:59`;
      try {
        const res = await recordingAPI.list(params);
        this.recordings = res.data;
      } catch (err) {
        this.loadError = err?.response?.data?.detail || err?.message || "Network error";
      } finally {
        this.loading = false;
      }
    },
    resetFilters() {
      this.filters = { cameraId: "", from: "", to: "" };
      this.loadRecordings();
    },
    toggleExpanded(id) {
      this.expanded = this.expanded === id ? null : id;
    },
    downloadUrl(id) {
      return recordingAPI.fileUrl(id);
    },
    cameraName(id) {
      return this.cameras.find((c) => c.id === id)?.name || `Camera #${id}`;
    },
    formatDateTime(iso) {
      const d = new Date(iso);
      return d.toLocaleString();
    },
    formatDuration(seconds) {
      if (seconds == null) return "in progress";
      if (seconds < 60) return `${seconds}s`;
      const m = Math.floor(seconds / 60);
      const s = seconds % 60;
      return `${m}m ${s}s`;
    },
    formatSize(bytes) {
      if (!bytes) return "0 B";
      const units = ["B", "KB", "MB", "GB"];
      let v = bytes;
      let i = 0;
      while (v >= 1024 && i < units.length - 1) {
        v /= 1024;
        i++;
      }
      return `${v.toFixed(v < 10 ? 1 : 0)} ${units[i]}`;
    },
    async deleteRecording(rec) {
      if (!window.confirm("Delete this recording?")) return;
      try {
        await recordingAPI.remove(rec.id);
      } catch (err) {
        alert(err?.response?.data?.detail || "Delete failed");
      }
      this.loadRecordings();
    },
  },
};
</script>

<style scoped>
.page-header {
  margin-bottom: 1.5rem;
}
.subtitle {
  color: var(--text-muted);
  margin: 0;
}
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1rem;
  align-items: end;
  margin-bottom: 1rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 160px;
}
.field > span {
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 500;
}
.reset {
  margin-left: auto;
}
.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
}
.danger-card {
  border-color: rgba(248, 113, 113, 0.35);
}
.recording-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.recording-row {
  padding: 0.85rem 1.1rem;
}
.row-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  cursor: pointer;
}
.row-title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text);
}
.row-meta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-top: 0.2rem;
}
.muted {
  color: var(--text-dim);
}
.row-actions {
  display: flex;
  gap: 0.5rem;
}
.small {
  padding: 0.35rem 0.7rem;
  font-size: 0.85rem;
}
.player {
  margin-top: 0.85rem;
  background: #000;
  border-radius: var(--radius-sm);
  overflow: hidden;
  aspect-ratio: 16 / 9;
}
.player video {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
}
</style>
