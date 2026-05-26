import { reactive } from "vue";

import client from "./client";

const TOKEN_KEY = "pi-nvr-token";
const USER_KEY = "pi-nvr-user";

function loadFromStorage() {
  try {
    return {
      token: localStorage.getItem(TOKEN_KEY) || null,
      user: JSON.parse(localStorage.getItem(USER_KEY) || "null"),
    };
  } catch {
    return { token: null, user: null };
  }
}

export const authState = reactive(loadFromStorage());

export function isAuthenticated() {
  return !!authState.token;
}

function persist() {
  if (authState.token) {
    localStorage.setItem(TOKEN_KEY, authState.token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
  if (authState.user) {
    localStorage.setItem(USER_KEY, JSON.stringify(authState.user));
  } else {
    localStorage.removeItem(USER_KEY);
  }
}

export async function login(username, password) {
  const res = await client.post("/api/auth/login", { username, password });
  authState.token = res.data.access_token;
  persist();
  const me = await client.get("/api/auth/me");
  authState.user = me.data;
  persist();
  return authState.user;
}

export function logout() {
  authState.token = null;
  authState.user = null;
  persist();
}

export function getToken() {
  return authState.token;
}
