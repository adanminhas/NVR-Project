import { createRouter, createWebHistory } from "vue-router";
import CameraList from "./pages/CameraList.vue";
import LiveView from "./pages/LiveView.vue";

const routes = [
  { path: "/", name: "cameras", component: CameraList },
  { path: "/live/:id", name: "live", component: LiveView, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
