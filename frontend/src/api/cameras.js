import client from "./client";

const PATH = "/api/cameras/";

export default {
  list() {
    return client.get(PATH);
  },
  get(id) {
    return client.get(`${PATH}${id}`);
  },
  create({ name, rtsp_url }) {
    return client.post(PATH, { name, rtsp_url });
  },
  update(id, payload) {
    return client.put(`${PATH}${id}`, payload);
  },
  remove(id) {
    return client.delete(`${PATH}${id}`);
  },
};
