import axios from "axios";

const API = "http://localhost:8000/api/streams";

export default {
  start(id) {
    return axios.post(`${API}/${id}/start`);
  },
  stop(id) {
    return axios.post(`${API}/${id}/stop`);
  },
};
