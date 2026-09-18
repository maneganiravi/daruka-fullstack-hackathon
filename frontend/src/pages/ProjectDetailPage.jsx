import React, { useEffect, useState, useCallback } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Navbar } from "../components/common/Navbar";
import { Modal } from "../components/common/Modal";
import { MapboxGLView } from "../components/map/MapboxGLView";
import { PolygonDrawer } from "../components/map/PolygonDrawer";
import { CarbonTrendChart } from "../components/charts/CarbonTrendChart";
import { BiodiversityChart } from "../components/charts/BiodiversityChart";
import { projectService } from "../services/projectService";
import { siteService } from "../services/siteService";
import { analyticsService } from "../services/analyticsService";
import { useAuth } from "../context/AuthContext";
import { ArrowLeft, Plus, Trash2 } from "lucide-react";

export const ProjectDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();

  const [project, setProject] = useState(null);
  const [sitesGeoJSON, setSitesGeoJSON] = useState(null);
  const [selectedSite, setSelectedSite] = useState(null);
  const [siteAnalyticsData, setSiteAnalyticsData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Add Site Modal State
  const [isAddSiteOpen, setIsAddSiteOpen] = useState(false);
  const [siteName, setSiteName] = useState("");
  const [siteDesc, setSiteDesc] = useState("");
  const [soilType, setSoilType] = useState("Red Laterite Loam");
  const [elevation, setElevation] = useState("");
  const [drawnGeometry, setDrawnGeometry] = useState(null);
  const [drawnArea, setDrawnArea] = useState(0.0);
  const [savingSite, setSavingSite] = useState(false);

  const fetchProjectData = useCallback(async () => {
    try {
      const [projData, geojson] = await Promise.all([
        projectService.getProjectDetails(id),
        siteService.getSitesGeoJSON(id),
      ]);
      setProject(projData);
      setSitesGeoJSON(geojson);

      // Auto select first site for analytics chart
      if (projData.sites && projData.sites.length > 0) {
        const firstSite = projData.sites[0];
        setSelectedSite(firstSite);
        const timeSeries = await analyticsService.getSiteTimeSeries(firstSite.id);
        setSiteAnalyticsData(timeSeries.data || []);
      }
    } catch (err) {
      console.error("Error loading project details:", err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchProjectData();
  }, [fetchProjectData]);

  const handleSelectSite = async (site) => {
    setSelectedSite(site);
    try {
      const timeSeries = await analyticsService.getSiteTimeSeries(site.id || site.site_id);
      setSiteAnalyticsData(timeSeries.data || []);
    } catch (err) {
      console.error("Error loading site analytics:", err);
    }
  };

  const handleCreateSite = async (e) => {
    e.preventDefault();
    if (!drawnGeometry) {
      alert("Please draw a polygon boundary on the map before saving the site.");
      return;
    }

    setSavingSite(true);
    try {
      await siteService.createSite({
        project_id: id,
        name: siteName,
        description: siteDesc,
        geometry: drawnGeometry,
        area_hectares: drawnArea,
        soil_type: soilType,
        elevation_meters: parseFloat(elevation) || 0.0,
      });

      setIsAddSiteOpen(false);
      setSiteName("");
      setSiteDesc("");
      setElevation("");
      setDrawnGeometry(null);
      setDrawnArea(0.0);
      fetchProjectData();
    } catch (err) {
      console.error("Error saving site polygon:", err);
      alert("Failed to save site polygon. Check polygon coordinates.");
    } finally {
      setSavingSite(false);
    }
  };

  const handleDeleteSite = async (siteId) => {
    if (!window.confirm("Are you sure you want to delete this geographical site?")) return;
    try {
      await siteService.deleteSite(siteId);
      fetchProjectData();
    } catch (err) {
      console.error("Failed to delete site:", err);
    }
  };

  const handleDeleteProject = async () => {
    if (!window.confirm("Are you sure you want to delete this entire project and its sites?")) return;
    try {
      await projectService.deleteProject(id);
      navigate("/projects");
    } catch (err) {
      console.error("Failed to delete project:", err);
    }
  };

  if (loading || !project) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <Navbar />
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)" }}>
          Loading restoration project details...
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />

      <main style={{ flex: 1, padding: "32px 24px", maxWidth: "1400px", margin: "0 auto", width: "100%" }}>
        {/* Breadcrumb Back */}
        <Link
          to="/projects"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
            color: "var(--text-muted)",
            fontSize: "0.85rem",
            textDecoration: "none",
            marginBottom: "16px",
          }}
        >
          <ArrowLeft size={16} /> Back to Projects
        </Link>

        {/* Project Header Banner */}
        <div
          className="glass-panel"
          style={{
            padding: "28px 32px",
            marginBottom: "28px",
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "20px",
          }}
        >
          <div style={{ flex: "1 1 500px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
              <span className={`badge badge-${project.status}`}>
                {project.status}
              </span>
              {project.client_name && (
                <span style={{ fontSize: "0.85rem", color: "var(--emerald-400)", fontWeight: 600 }}>
                  🏢 {project.client_name}
                </span>
              )}
            </div>

            <h1 style={{ fontSize: "1.8rem", fontWeight: 800, color: "#ffffff" }}>
              {project.name}
            </h1>

            <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", marginTop: "8px", lineHeight: 1.5 }}>
              {project.description || "No project description provided."}
            </p>
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={() => setIsAddSiteOpen(true)}
              className="btn btn-primary"
            >
              <Plus size={18} /> Add Site Polygon
            </button>
            {isAdmin && (
              <button
                onClick={handleDeleteProject}
                className="btn btn-danger btn-sm"
                title="Delete Project"
              >
                <Trash2 size={16} />
              </button>
            )}
          </div>
        </div>

        {/* Top Summary Metrics */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "28px" }}>
          <div className="glass-card" style={{ padding: "18px 20px" }}>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600 }}>Total Mapped Area</span>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "var(--emerald-400)", marginTop: "4px" }}>
              {project.total_area_hectares} <span style={{ fontSize: "0.85rem" }}>ha</span>
            </div>
          </div>
          <div className="glass-card" style={{ padding: "18px 20px" }}>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600 }}>Carbon Sequestered</span>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "var(--cyan-400)", marginTop: "4px" }}>
              {project.total_carbon_stored_tons} <span style={{ fontSize: "0.85rem" }}>tons CO₂</span>
            </div>
          </div>
          <div className="glass-card" style={{ padding: "18px 20px" }}>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600 }}>Target Carbon Sequestration</span>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "#ffffff", marginTop: "4px" }}>
              {project.target_carbon_sequestration_tons?.toLocaleString() || 0} <span style={{ fontSize: "0.85rem" }}>tons</span>
            </div>
          </div>
          <div className="glass-card" style={{ padding: "18px 20px" }}>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 600 }}>Geographical Sites</span>
            <div style={{ fontSize: "1.6rem", fontWeight: 800, color: "var(--purple-400)", marginTop: "4px" }}>
              {project.sites?.length || 0} <span style={{ fontSize: "0.85rem" }}>sectors</span>
            </div>
          </div>
        </div>

        {/* Map & Sites List Section */}
        <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: "24px", marginBottom: "28px" }}>
          {/* Project Map */}
          <div className="glass-panel" style={{ padding: "20px" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff", marginBottom: "12px" }}>
              Project Site Boundaries (PostGIS)
            </h3>
            <MapboxGLView
              sitesGeoJSON={sitesGeoJSON}
              height="420px"
              onSiteClick={(props) => {
                const matched = project.sites?.find((s) => s.id === props.site_id);
                if (matched) handleSelectSite(matched);
              }}
            />
          </div>

          {/* Attached Sites List */}
          <div className="glass-panel" style={{ padding: "20px", display: "flex", flexDirection: "column" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "#ffffff" }}>
                Attached Geographical Sites
              </h3>
              <button
                onClick={() => setIsAddSiteOpen(true)}
                className="btn btn-sm btn-primary"
              >
                <Plus size={14} /> New Site
              </button>
            </div>

            <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "10px", maxHeight: "360px" }}>
              {project.sites?.map((site) => {
                const isSelected = selectedSite?.id === site.id;
                return (
                  <div
                    key={site.id}
                    onClick={() => handleSelectSite(site)}
                    className="glass-card"
                    style={{
                      padding: "14px 16px",
                      cursor: "pointer",
                      border: isSelected ? "1px solid var(--emerald-400)" : "1px solid var(--border-color)",
                      background: isSelected ? "rgba(16, 185, 129, 0.1)" : "rgba(15, 23, 42, 0.6)",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: isSelected ? "var(--emerald-400)" : "#ffffff" }}>
                        📍 {site.name}
                      </h4>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteSite(site.id);
                        }}
                        style={{
                          background: "transparent",
                          border: "none",
                          color: "var(--text-muted)",
                          cursor: "pointer",
                          padding: "4px",
                        }}
                        title="Delete site"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "12px", fontSize: "0.78rem", color: "var(--text-secondary)", marginTop: "6px" }}>
                      <span>Area: <strong style={{ color: "#ffffff" }}>{site.area_hectares} ha</strong></span>
                      <span>Carbon: <strong style={{ color: "var(--emerald-400)" }}>{site.latest_carbon_stored || 0} t</strong></span>
                      <span>Bio Score: <strong style={{ color: "var(--purple-400)" }}>{site.latest_biodiversity_score || 0}%</strong></span>
                    </div>
                  </div>
                );
              })}

              {(!project.sites || project.sites.length === 0) && (
                <div style={{ padding: "40px 20px", textAlign: "center", color: "var(--text-muted)" }}>
                  No geographical sites added yet. Click "Add Site Polygon" to draw site boundaries.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Selected Site Time-Series Charts */}
        {selectedSite && (
          <div className="glass-panel" style={{ padding: "28px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "20px", flexWrap: "wrap", gap: "10px" }}>
              <div>
                <span style={{ fontSize: "0.75rem", textTransform: "uppercase", fontWeight: 700, color: "var(--emerald-400)" }}>
                  Environmental Analytics Over Time
                </span>
                <h3 style={{ fontSize: "1.3rem", fontWeight: 800, color: "#ffffff" }}>
                  {selectedSite.name}
                </h3>
              </div>
              <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                Soil: <strong style={{ color: "#ffffff" }}>{selectedSite.soil_type || "Loam"}</strong> | Elevation: <strong style={{ color: "#ffffff" }}>{selectedSite.elevation_meters || 0} m</strong>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
              <div style={{ background: "rgba(0,0,0,0.2)", padding: "18px", borderRadius: "var(--radius-md)" }}>
                <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff", marginBottom: "12px" }}>
                  Carbon Sequestration Trajectory (Chart.js)
                </h4>
                <CarbonTrendChart dataPoints={siteAnalyticsData} />
              </div>

              <div style={{ background: "rgba(0,0,0,0.2)", padding: "18px", borderRadius: "var(--radius-md)" }}>
                <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff", marginBottom: "12px" }}>
                  Biodiversity Health & Canopy Cover (Chart.js)
                </h4>
                <BiodiversityChart dataPoints={siteAnalyticsData} />
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Add Site Polygon Modal */}
      <Modal
        isOpen={isAddSiteOpen}
        onClose={() => setIsAddSiteOpen(false)}
        title="Draw & Save Site Boundary (PostGIS)"
        maxWidth="800px"
      >
        <form onSubmit={handleCreateSite}>
          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "16px", marginBottom: "16px" }}>
            <div className="input-group">
              <label className="input-label">Site Name *</label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g. Wayanad Sector 4 Corridor"
                value={siteName}
                onChange={(e) => setSiteName(e.target.value)}
                required
              />
            </div>
            <div className="input-group">
              <label className="input-label">Soil Classification</label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g. Laterite High-Humus"
                value={soilType}
                onChange={(e) => setSoilType(e.target.value)}
              />
            </div>
          </div>

          <div className="input-group" style={{ marginBottom: "16px" }}>
            <label className="input-label">Elevation (meters)</label>
            <input
              type="number"
              className="input-field"
              placeholder="e.g. 920"
              value={elevation}
              onChange={(e) => setElevation(e.target.value)}
            />
          </div>

          {/* Embedded Interactive Mapbox Polygon Drawer */}
          <div style={{ marginBottom: "16px" }}>
            <label className="input-label" style={{ display: "block", marginBottom: "8px" }}>
              Draw Polygon Boundary On Map (Live Area Calculation) *
            </label>
            <PolygonDrawer
              onPolygonCreated={(geometry, area) => {
                setDrawnGeometry(geometry);
                setDrawnArea(area);
              }}
              height="340px"
            />
          </div>

          <div className="input-group">
            <label className="input-label">Site Description</label>
            <textarea
              className="input-field"
              placeholder="Ecological notes, flora/fauna species observed, terrain details..."
              value={siteDesc}
              onChange={(e) => setSiteDesc(e.target.value)}
              style={{ minHeight: "60px" }}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "20px" }}>
            <button
              type="button"
              onClick={() => setIsAddSiteOpen(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={savingSite || !drawnGeometry}
            >
              {savingSite ? "Storing in PostGIS..." : `Save Site (${drawnArea} ha)`}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
