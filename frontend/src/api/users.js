import client from "./client";

const PATH = "/api/users/";

export default {
  list() {
    return client.get(PATH);
  },
  create({ username, password, is_admin = false }) {
    return client.post(PATH, { username, password, is_admin });
  },
  changePassword(id, password) {
    return client.put(`${PATH}${id}/password`, { password });
  },
  remove(id) {
    return client.delete(`${PATH}${id}`);
  },
};
