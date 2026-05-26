import { createRouter, createWebHistory } from "vue-router";

import { authState, isAuthenticated } from "./api/auth";
import CameraList from "./pages/CameraList.vue";
import LiveView from "./pages/LiveView.vue";
import Login from "./pages/Login.vue";
import Recordings from "./pages/Recordings.vue";
import Users from "./pages/Users.vue";

const routes = [
  { path: "/", redirect: "/cameras" },
  { path: "/login", name: "login", component: Login, meta: { public: true } },
  { path: "/cameras", name: "cameras", component: CameraList },
  { path: "/recordings", name: "recordings", component: Recordings },
  { path: "/live/:id", name: "live", component: LiveView, props: true },
  {
    path: "/users",
    name: "users",
    component: Users,
    meta: { adminOnly: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.meta.public) return true;
  if (!isAuthenticated()) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.meta.adminOnly && !authState.user?.is_admin) {
    return { name: "cameras" };
  }
  return true;
});

export default router;
