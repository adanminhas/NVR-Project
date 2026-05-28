import axios from "axios";

function resolveBaseURL() {
  const envURL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "");
  const inBrowser = typeof window !== "undefined" && window.location;

  if (inBrowser) {
    const { protocol, hostname } = window.location;
    const derived = `${protocol}//${hostname}:8000`;
    const localHosts = ["localhost", "127.0.0.1"];

    // If an env URL is set but points at localhost while the page itself is
    // being viewed from a non-localhost host (e.g. a phone hitting the PC's
    // LAN IP), prefer the derived URL so the API call goes back to the same
    // server that served the page.
    if (envURL) {
      try {
        const envHost = new URL(envURL).hostname;
        if (localHosts.includes(envHost) && !localHosts.includes(hostname)) {
          return derived;
        }
      } catch {
        // Unparseable env URL — fall back to using it raw.
      }
      return envURL;
    }
    return derived;
  }

  return envURL || "http://localhost:8000";
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
