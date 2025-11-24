import axios from "axios";

const API = "http://localhost:8000/api/cameras";

export default {
  list() {
    return axios.get(API);
  },
};
