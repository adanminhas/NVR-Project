import client, { API_BASE_URL } from "./client";

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
    return `${API_BASE_URL}${PATH}${id}/file`;
  },
};
