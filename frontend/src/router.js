import { createRouter, createWebHistory } from "vue-router";
import CameraList from "./pages/CameraList.vue";
import LiveView from "./pages/LiveView.vue";
import Recordings from "./pages/Recordings.vue";

const routes = [
  { path: "/", redirect: "/cameras" },
  { path: "/cameras", name: "cameras", component: CameraList },
  { path: "/recordings", name: "recordings", component: Recordings },
  { path: "/live/:id", name: "live", component: LiveView, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
