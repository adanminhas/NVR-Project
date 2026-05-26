import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { configureClient } from "./api/client";
import { authState, getToken, logout } from "./api/auth";
import "./style.css";

configureClient({
  tokenGetter: getToken,
  unauthorizedHandler: () => {
    if (!authState.token) return;
    logout();
    if (router.currentRoute.value.name !== "login") {
      router.replace({
        name: "login",
        query: { redirect: router.currentRoute.value.fullPath },
      });
    }
  },
});

createApp(App).use(router).mount("#app");
