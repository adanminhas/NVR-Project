<template>
  <div class="page">
    <h2>Live View (Camera {{ id }})</h2>

    <video id="video" controls autoplay></video>
  </div>
</template>

<script>
import Hls from "hls.js";

export default {
  props: ["id"],
  mounted() {
    const video = document.getElementById("video");
    const playlist = `http://localhost:8000/streams/${this.id}/index.m3u8`;

    if (Hls.isSupported()) {
      const hls = new Hls();
      hls.loadSource(playlist);
      hls.attachMedia(video);
    } else {
      video.src = playlist;
    }
  },
};
</script>

<style>
.page { padding: 20px; }
video { width: 100%; max-width: 800px; border-radius: 8px; }
</style>
