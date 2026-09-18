import api from "./api";

export const analyticsService = {
  async getDashboardMetrics() {
    const response = await api.get("/analytics/dashboard");
    return response.data;
  },

  async getSiteTimeSeries(siteId) {
    const response = await api.get(`/analytics/sites/${siteId}`);
    return response.data;
  },

  async addSiteMetric(siteId, metricData) {
    const response = await api.post(`/analytics/sites/${siteId}`, metricData);
    return response.data;
  },
};
