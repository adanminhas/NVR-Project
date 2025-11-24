<template>
  <div class="page">
    <h2>Cameras</h2>

    <div class="camera-grid">
      <div v-for="cam in cameras" :key="cam.id" class="camera-card">
        <h3>{{ cam.name }}</h3>
        <p>Status: {{ cam.status }}</p>

        <div class="buttons">
          <button @click="startStream(cam.id)">Start</button>
          <button @click="stopStream(cam.id)">Stop</button>
          <router-link :to="`/live/${cam.id}`">
            <button>Live View</button>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import cameraAPI from "../api/cameras";
import streamAPI from "../api/streams";

export default {
  data() {
    return {
      cameras: [],
    };
  },
  mounted() {
    this.loadCameras();
  },
  methods: {
    async loadCameras() {
      const res = await cameraAPI.list();
      this.cameras = res.data;
    },
    async startStream(id) {
      await streamAPI.start(id);
      this.loadCameras();
    },
    async stopStream(id) {
      await streamAPI.stop(id);
      this.loadCameras();
    },
  },
};
</script>

<style>
.page {
  padding: 20px;
}
.camera-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}
.camera-card {
  background: #222;
  padding: 20px;
  border-radius: 8px;
  color: white;
}
button {
  margin-right: 10px;
  padding: 8px 12px;
  border: none;
  background: #42b883;
  color: white;
  border-radius: 6px;
  cursor: pointer;
}
button:hover {
  background: #369d6f;
}
</style>
