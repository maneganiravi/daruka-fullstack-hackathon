import api from "./api";

export const projectService = {
  async getProjects(params = {}) {
    const response = await api.get("/projects", { params });
    return response.data;
  },

  async getProjectDetails(projectId) {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },

  async createProject(projectData) {
    const response = await api.post("/projects", projectData);
    return response.data;
  },

  async updateProject(projectId, updateData) {
    const response = await api.put(`/projects/${projectId}`, updateData);
    return response.data;
  },

  async deleteProject(projectId) {
    const response = await api.delete(`/projects/${projectId}`);
    return response.data;
  },
};
