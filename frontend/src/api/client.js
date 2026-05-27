import axios from "axios";

function resolveBaseURL() {
  const envURL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "");
  if (envURL) return envURL;
  // Fallback: derive from the page origin so the app works on LAN/mobile
  // when accessed via the host's IP — assumes the backend runs on port 8000
  // of the same host.
  if (typeof window !== "undefined" && window.location) {
    const { protocol, hostname } = window.location;
    return `${protocol}//${hostname}:8000`;
  }
  return "http://localhost:8000";
}

const baseURL = resolveBaseURL();

const client = axios.create({ baseURL });

let onUnauthorized = null;
let getAuthToken = () => null;

export function configureClient({ tokenGetter, unauthorizedHandler }) {
  if (tokenGetter) getAuthToken = tokenGetter;
  if (unauthorizedHandler) onUnauthorized = unauthorizedHandler;
}

client.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401 && onUnauthorized) {
      onUnauthorized();
    }
    return Promise.reject(error);
  },
);

export const API_BASE_URL = baseURL;
export default client;
