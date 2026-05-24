import client, { API_BASE_URL } from "./client";

const PATH = "/api/streams";

export default {
  start(id) {
    return client.post(`${PATH}/${id}/start`);
  },
  stop(id) {
    return client.post(`${PATH}/${id}/stop`);
  },
  health(id) {
    return client.get(`${PATH}/${id}/health`);
  },
  playlistUrl(id) {
    return `${API_BASE_URL}/streams/${id}/index.m3u8`;
  },
};
