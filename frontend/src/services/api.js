import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor: attach JWT token if present in localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("daruka_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token on 401
      localStorage.removeItem("daruka_token");
      localStorage.removeItem("daruka_user");
    }
    return Promise.reject(error);
  }
);

export const getErrorMessage = (error, defaultMsg = "An unexpected error occurred. Please try again.") => {
  if (!error) return defaultMsg;
  if (!error.response) {
    return "Cannot connect to server. Please ensure the backend server is running at http://127.0.0.1:8001.";
  }
  const detail = error.response.data?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail.map((d) => (typeof d === "string" ? d : d.msg || JSON.stringify(d))).join("; ");
  }
  if (typeof detail === "object" && detail !== null) {
    return detail.msg || JSON.stringify(detail);
  }
  return error.response.data?.message || defaultMsg;
};

export default api;
