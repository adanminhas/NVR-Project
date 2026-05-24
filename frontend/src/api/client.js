import axios from "axios";

const baseURL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

const client = axios.create({ baseURL });

export const API_BASE_URL = baseURL;
export default client;
