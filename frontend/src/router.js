import { createRouter, createWebHistory } from "vue-router";
import CameraList from "./pages/CameraList.vue";
import LiveView from "./pages/LiveView.vue";

const routes = [
  { path: "/", redirect: "/cameras" },   // <--- FIX #1
  { path: "/cameras", name: "cameras", component: CameraList },  // <--- FIX #2
  { path: "/live/:id", name: "live", component: LiveView, props: true }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
