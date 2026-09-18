import api from "./api";

export const siteService = {
  async getSitesGeoJSON(projectId = null) {
    const params = projectId ? { project_id: projectId } : {};
    const response = await api.get("/sites/geojson", { params });
    return response.data;
  },

  async getSitesList(projectId = null) {
    const params = projectId ? { project_id: projectId } : {};
    const response = await api.get("/sites", { params });
    return response.data;
  },

  async getSiteDetails(siteId) {
    const response = await api.get(`/sites/${siteId}`);
    return response.data;
  },

  async createSite(siteData) {
    const response = await api.post("/sites", siteData);
    return response.data;
  },

  async updateSite(siteId, updateData) {
    const response = await api.put(`/sites/${siteId}`, updateData);
    return response.data;
  },

  async deleteSite(siteId) {
    const response = await api.delete(`/sites/${siteId}`);
    return response.data;
  },
};
