import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

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
