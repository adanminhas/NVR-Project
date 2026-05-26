import client, { API_BASE_URL } from "./client";
import { getToken } from "./auth";

const PATH = "/api/recordings/";

export default {
  list(params = {}) {
    return client.get(PATH, { params });
  },
  get(id) {
    return client.get(`${PATH}${id}`);
  },
  remove(id) {
    return client.delete(`${PATH}${id}`);
  },
  fileUrl(id) {
    // <video> tag can't send Authorization header; embed token in query string.
    const token = encodeURIComponent(getToken() || "");
    return `${API_BASE_URL}${PATH}${id}/file?token=${token}`;
  },
};
