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

      <div v-if="overlay" class="overlay">
        <p>{{ overlay }}</p>
        <button v-if="canRetry" class="btn-primary" @click="reloadPlayer">
          Retry
        </button>
      </div>
    </div>

    <details v-if="health" class="diagnostics card">
      <summary>Diagnostics</summary>
      <dl>
        <dt>ffmpeg running</dt>
        <dd>{{ health.ffmpeg_running ? "yes" : "no" }}</dd>
        <dt>Playlist age</dt>
        <dd>{{ formatAge(health.playlist_age_seconds) }}</dd>
        <dt>Last segment age</dt>
        <dd>{{ formatAge(health.last_segment_age_seconds) }}</dd>
      </dl>
      <pre v-if="health.recent_log_lines?.length" class="log">{{
        health.recent_log_lines.join("")
      }}</pre>
    </details>
  </section>
</template>

<script>
import Hls from "hls.js";
import streamAPI from "../api/streams";

export default {
  props: ["id"],

  data() {
    return {
      cameraId: this.id,
      hls: null,
      healthInterval: null,
      health: null,
      loading: true,
      hlsError: "",
    };
  },

  computed: {
    healthLabel() {
      if (this.hlsError) return "error";
      if (!this.health) return "connecting";
      if (this.health.is_live) return "live";
      if (this.health.ffmpeg_running) return "starting";
      return "offline";
    },
    healthBadgeClass() {
      switch (this.healthLabel) {
        case "live":
          return "success";
        case "starting":
        case "connecting":
          return "warning";
        case "offline":
        case "error":
          return "danger";
        default:
          return "muted";
      }
    },
    overlay() {
      if (this.hlsError) return this.hlsError;
      if (this.healthLabel === "connecting") return "Connecting…";
      if (this.healthLabel === "starting")
        return "Stream is starting — first segments take a few seconds…";
      if (this.healthLabel === "offline")
        return "Stream is offline. Click Start on the Cameras page.";
      return "";
    },
    canRetry() {
      return !!this.hlsError || this.healthLabel === "offline";
    },
  },

  mounted() {
    // Wait until ffmpeg is producing segments before initializing hls.js.
    // Otherwise the player races the first segments and ends up in a stuck
    // state requiring a manual refresh.
    this.healthInterval = setInterval(this.checkHealth, 2000);
    this.checkHealth();
  },

  beforeUnmount() {
    if (this.hls) this.hls.destroy();
    clearInterval(this.healthInterval);
  },

  methods: {
    startStream() {
      const video = this.$refs.videoPlayer;
      const streamUrl = streamAPI.playlistUrl(this.cameraId);
      this.hlsError = "";

      if (Hls.isSupported()) {
        this.hls = new Hls({
          // Buffer more aggressively to ride out ffmpeg hiccups.
          maxBufferLength: 30,
          maxMaxBufferLength: 60,
          maxBufferSize: 60 * 1000 * 1000,
          // Stay a few seconds back from live edge instead of right on it.
          liveSyncDuration: 6,
          liveMaxLatencyDuration: 30,
          manifestLoadingMaxRetry: 6,
          manifestLoadingRetryDelay: 1000,
          levelLoadingMaxRetry: 6,
          fragLoadingMaxRetry: 6,
        });
        this.hls.loadSource(streamUrl);
        this.hls.attachMedia(video);
        this.hls.on(Hls.Events.ERROR, (_, data) => {
          if (!data.fatal) return;
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              // Segment/playlist missed — keep trying instead of giving up.
              this.hls.startLoad();
              break;
            case Hls.ErrorTypes.MEDIA_ERROR:
              this.hls.recoverMediaError();
              break;
            default:
              this.hlsError = `Playback error: ${data.details}`;
          }
        });
      } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
        video.src = streamUrl;
      } else {
        this.hlsError = "HLS is not supported in this browser.";
      }
    },
    async checkHealth() {
      try {
        const res = await streamAPI.health(this.cameraId);
        this.health = res.data;

        const playerNotStarted = !this.hls && this.$refs.videoPlayer;
        const readyToStart =
          this.health.ffmpeg_running && this.health.playlist_exists;

        if (playerNotStarted && readyToStart) {
          this.startStream();
        } else if (this.hlsError && this.health.is_live) {
          // Rebuild only if we errored AND ffmpeg is producing fresh segments.
          this.reloadPlayer();
        }
      } catch (err) {
        this.health = null;
        this.hlsError =
          err?.response?.data?.detail || err?.message || "Health check failed";
      }
    },
    reloadPlayer({ silent = false } = {}) {
      if (!silent) this.hlsError = "";
      if (this.hls) {
        this.hls.destroy();
        this.hls = null;
      }
      this.startStream();
    },
    formatAge(seconds) {
      if (seconds == null) return "—";
      if (seconds < 1) return "just now";
      if (seconds < 60) return `${seconds.toFixed(1)}s ago`;
      return `${Math.floor(seconds / 60)}m ${Math.floor(seconds % 60)}s ago`;
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
  position: relative;
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
.overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  background: rgba(11, 18, 32, 0.7);
  color: var(--text);
  padding: 1rem;
  text-align: center;
}
.overlay p {
  color: var(--text);
  margin: 0;
}
.diagnostics {
  margin-top: 1rem;
  padding: 1rem 1.25rem;
}
.diagnostics summary {
  cursor: pointer;
  color: var(--text-muted);
  font-weight: 500;
}
.diagnostics dl {
  display: grid;
  grid-template-columns: 200px 1fr;
  row-gap: 0.4rem;
  column-gap: 0.75rem;
  margin: 0.75rem 0 0;
  font-size: 0.9rem;
}
.diagnostics dt {
  color: var(--text-muted);
}
.diagnostics dd {
  margin: 0;
  color: var(--text);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
.log {
  margin: 0.75rem 0 0;
  padding: 0.75rem;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  color: var(--text-muted);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  max-height: 200px;
  overflow: auto;
  white-space: pre-wrap;
}
</style>
