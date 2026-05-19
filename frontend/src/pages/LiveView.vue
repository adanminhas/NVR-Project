<template>
  <section class="page">
    <header class="live-header">
      <button class="btn-ghost" @click="$router.push('/cameras')">
        ← Back
      </button>
      <div class="live-title">
        <h2>Live View</h2>
        <p class="subtitle">Camera #{{ cameraId }}</p>
      </div>
      <span class="badge" :class="healthBadgeClass">{{ healthLabel }}</span>
    </header>

    <div class="video-wrapper card">
      <video
        ref="videoPlayer"
        controls
        autoplay
        muted
        playsinline
      ></video>
    </div>
  </section>
</template>

<script>
import Hls from "hls.js";

export default {
  props: ["id"],

  data() {
    return {
      cameraId: this.id,
      hls: null,
      healthInterval: null,
      health: null,
    };
  },

  computed: {
    healthLabel() {
      if (!this.health) return "connecting";
      if (this.health.ffmpeg_running && this.health.hls_active) return "live";
      if (this.health.ffmpeg_running) return "starting";
      return "offline";
    },
    healthBadgeClass() {
      switch (this.healthLabel) {
        case "live":
          return "success";
        case "starting":
          return "warning";
        case "offline":
          return "danger";
        default:
          return "muted";
      }
    },
  },

  mounted() {
    this.startStream();
    this.healthInterval = setInterval(this.checkHealth, 5000);
  },

  beforeUnmount() {
    if (this.hls) this.hls.destroy();
    clearInterval(this.healthInterval);
  },

  methods: {
    startStream() {
      const video = this.$refs.videoPlayer;
      const streamUrl = `http://localhost:8000/streams/${this.cameraId}/index.m3u8`;

      if (Hls.isSupported()) {
        this.hls = new Hls({
          maxBufferLength: 5,
          liveSyncDuration: 2,
          maxBufferSize: 10 * 1000 * 1000,
        });
        this.hls.loadSource(streamUrl);
        this.hls.attachMedia(video);
        this.hls.on(Hls.Events.ERROR, (_, data) => {
          console.warn("HLS error:", data);
        });
      } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
        video.src = streamUrl;
      }
    },
    async checkHealth() {
      try {
        const res = await fetch(
          `http://localhost:8000/api/streams/${this.cameraId}/health`
        );
        const data = await res.json();
        this.health = data;
        if (!data.ffmpeg_running || !data.hls_active) {
          this.reloadPlayer();
        }
      } catch (err) {
        console.error("Health check failed", err);
        this.health = { ffmpeg_running: false, hls_active: false };
      }
    },
    reloadPlayer() {
      if (this.hls) {
        this.hls.destroy();
        this.hls = null;
      }
      this.startStream();
    },
  },
};
</script>

<style scoped>
.live-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.live-title h2 {
  margin: 0 0 0.1rem;
}
.subtitle {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.9rem;
}
.live-header > .badge {
  margin-left: auto;
}
.video-wrapper {
  padding: 0;
  overflow: hidden;
  background: #000;
  aspect-ratio: 16 / 9;
}
video {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: contain;
  background: #000;
}
</style>
