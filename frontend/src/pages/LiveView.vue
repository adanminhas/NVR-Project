<template>
  <div class="page">
    <h2>Live View — Camera {{ cameraId }}</h2>

    <div class="video-wrapper">
      <video ref="videoPlayer" controls autoplay muted playsinline></video>
    </div>

    <button class="back-btn" @click="$router.push('/cameras')">
      ← Back to Cameras
    </button>
  </div>
</template>

<script>
import Hls from "hls.js";

export default {
  props: ["id"],

  data() {
    return {
      cameraId: this.id,
      hls: null,
    };
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

        if (!data.ffmpeg_running || !data.hls_active) {
          console.warn("Stream unhealthy, reloading HLS");
          this.reloadPlayer();
        }
      } catch (err) {
        console.error("Health check failed", err);
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

<style>
.page {
  padding: 20px;
  color: white;
}
.video-wrapper {
  width: 100%;
  max-width: 900px;
  margin: auto;
  background: black;
  border-radius: 10px;
}
video {
  width: 100%;
}
.back-btn {
  margin-top: 20px;
  padding: 10px 16px;
  border: none;
  background: #42b883;
  color: white;
  border-radius: 6px;
  cursor: pointer;
}
.back-btn:hover {
  background: #369d6f;
}
</style>
