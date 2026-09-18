import React, { useEffect, useState, useCallback } from "react";
import { Navbar } from "../components/common/Navbar";
import { MapboxGLView } from "../components/map/MapboxGLView";
import { PolygonDrawer } from "../components/map/PolygonDrawer";
import { Modal } from "../components/common/Modal";
import { CarbonTrendChart } from "../components/charts/CarbonTrendChart";
import { BiodiversityChart } from "../components/charts/BiodiversityChart";
import { siteService } from "../services/siteService";
import { projectService } from "../services/projectService";
import { analyticsService } from "../services/analyticsService";
import { Plus, Search, X } from "lucide-react";

export const MapExplorerPage = () => {
  const [sitesGeoJSON, setSitesGeoJSON] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [selectedSiteProps, setSelectedSiteProps] = useState(null);
  const [siteAnalytics, setSiteAnalytics] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const sidebarOpen = true;

  // Add Site Modal
  const [isAddSiteOpen, setIsAddSiteOpen] = useState(false);
  const [siteName, setSiteName] = useState("");
  const [siteDesc, setSiteDesc] = useState("");
  const [targetProject, setTargetProject] = useState("");
  const [soilType, setSoilType] = useState("Loam");
  const [drawnGeometry, setDrawnGeometry] = useState(null);
  const [drawnArea, setDrawnArea] = useState(0.0);
  const [saving, setSaving] = useState(false);

  const loadMapData = useCallback(async () => {
    try {
      const [geojson, projs] = await Promise.all([
        siteService.getSitesGeoJSON(selectedProjectId || null),
        projectService.getProjects(),
      ]);
      setSitesGeoJSON(geojson);
      setProjects(projs);
      if (projs.length > 0 && !targetProject) {
        setTargetProject(projs[0].id);
      }
    } catch (err) {
      console.error("Failed to load map data:", err);
    }
  }, [selectedProjectId, targetProject]);

  useEffect(() => {
    loadMapData();
  }, [loadMapData]);

  const handleSiteClick = async (props) => {
    setSelectedSiteProps(props);
    try {
      const ts = await analyticsService.getSiteTimeSeries(props.site_id);
      setSiteAnalytics(ts.data || []);
    } catch (err) {
      console.error("Failed to load site analytics:", err);
    }
  };

  const handleSaveSite = async (e) => {
    e.preventDefault();
    if (!drawnGeometry) {
      alert("Please draw a polygon boundary on the map first.");
      return;
    }

    setSaving(true);
    try {
      await siteService.createSite({
        project_id: targetProject,
        name: siteName,
        description: siteDesc,
        geometry: drawnGeometry,
        area_hectares: drawnArea,
        soil_type: soilType,
      });

      setIsAddSiteOpen(false);
      setSiteName("");
      setSiteDesc("");
      setDrawnGeometry(null);
      setDrawnArea(0.0);
      loadMapData();
    } catch (err) {
      console.error("Failed to create site:", err);
      alert("Error saving site. Check that geometry is valid.");
    } finally {
      setSaving(false);
    }
  };

  const filteredFeatures = sitesGeoJSON?.features?.filter((f) => {
    if (!searchQuery.trim()) return true;
    return (
      f.properties.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.properties.project_name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }) || [];

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", overflow: "hidden" }}>
      <Navbar />

      <div style={{ flex: 1, display: "flex", position: "relative", overflow: "hidden" }}>
        {/* Left GIS Sidebar */}
        <aside
          style={{
            width: sidebarOpen ? "340px" : "0px",
            transition: "width 0.3s cubic-bezier(0.16, 1, 0.3, 1)",
            backgroundColor: "rgba(10, 15, 29, 0.95)",
            borderRight: "1px solid var(--border-color)",
            display: "flex",
            flexDirection: "column",
            zIndex: 20,
            overflow: "hidden",
          }}
        >
          <div style={{ padding: "20px", borderBottom: "1px solid var(--border-color)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <h2 style={{ fontSize: "1.1rem", fontWeight: 800, color: "#ffffff" }}>
                GIS Layers & Sites
              </h2>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                {filteredFeatures.length} Polygons Loaded
              </div>
            </div>
            <button
              onClick={() => setIsAddSiteOpen(true)}
              className="btn btn-sm btn-primary"
            >
              <Plus size={14} /> Draw Site
            </button>
          </div>

          {/* Project Filter & Search */}
          <div style={{ padding: "16px", display: "flex", flexDirection: "column", gap: "10px", borderBottom: "1px solid var(--border-color)" }}>
            <select
              className="input-field"
              style={{ fontSize: "0.85rem", padding: "8px 12px" }}
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
            >
              <option value="" style={{ background: "#0f172a" }}>All Projects (Global)</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id} style={{ background: "#0f172a" }}>
                  {p.name}
                </option>
              ))}
            </select>

            <div style={{ position: "relative" }}>
              <Search size={14} color="var(--text-muted)" style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)" }} />
              <input
                type="text"
                placeholder="Search sites..."
                className="input-field"
                style={{ paddingLeft: "32px", fontSize: "0.85rem", padding: "6px 10px 6px 32px" }}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {/* Site Polygons List */}
          <div style={{ flex: 1, overflowY: "auto", padding: "12px", display: "flex", flexDirection: "column", gap: "8px" }}>
            {filteredFeatures.map((f) => {
              const p = f.properties;
              const isSelected = selectedSiteProps?.site_id === p.site_id;
              return (
                <div
                  key={p.site_id}
                  onClick={() => handleSiteClick(p)}
                  className="glass-card"
                  style={{
                    padding: "12px 14px",
                    cursor: "pointer",
                    border: isSelected ? "1px solid var(--emerald-400)" : "1px solid var(--border-color)",
                    background: isSelected ? "rgba(16, 185, 129, 0.15)" : "rgba(15, 23, 42, 0.6)",
                  }}
                >
                  <div style={{ fontSize: "0.7rem", color: "var(--emerald-400)", fontWeight: 700, textTransform: "uppercase" }}>
                    {p.project_name}
                  </div>
                  <h4 style={{ fontSize: "0.9rem", fontWeight: 700, color: "#ffffff", marginTop: "2px" }}>
                    📍 {p.name}
                  </h4>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--text-secondary)", marginTop: "6px" }}>
                    <span>{p.area_hectares} ha</span>
                    <strong style={{ color: "var(--emerald-400)" }}>{p.carbon_stored_tons} t CO₂</strong>
                  </div>
                </div>
              );
            })}
          </div>
        </aside>

        {/* Center Interactive Map */}
        <div style={{ flex: 1, position: "relative", height: "100%" }}>
          <MapboxGLView
            sitesGeoJSON={sitesGeoJSON}
            height="100%"
            onSiteClick={(props) => handleSiteClick(props)}
            showControls={true}
          />
        </div>

        {/* Right Site Inspection Drawer */}
        {selectedSiteProps && (
          <aside
            style={{
              width: "440px",
              backgroundColor: "rgba(10, 15, 29, 0.95)",
              backdropFilter: "blur(16px)",
              borderLeft: "1px solid var(--border-color)",
              padding: "24px",
              display: "flex",
              flexDirection: "column",
              overflowY: "auto",
              zIndex: 20,
              boxShadow: "var(--shadow-lg)",
            }}
          >
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "16px" }}>
              <div>
                <span style={{ fontSize: "0.7rem", textTransform: "uppercase", color: "var(--emerald-400)", fontWeight: 700 }}>
                  {selectedSiteProps.project_name}
                </span>
                <h3 style={{ fontSize: "1.25rem", fontWeight: 800, color: "#ffffff", marginTop: "2px" }}>
                  {selectedSiteProps.name}
                </h3>
              </div>
              <button
                onClick={() => setSelectedSiteProps(null)}
                style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Quick Specs */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "20px" }}>
              <div style={{ background: "rgba(0,0,0,0.3)", padding: "12px", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Polygon Area</span>
                <div style={{ fontSize: "1.2rem", fontWeight: 800, color: "#ffffff" }}>
                  {selectedSiteProps.area_hectares} ha
                </div>
              </div>
              <div style={{ background: "rgba(0,0,0,0.3)", padding: "12px", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Carbon Stored</span>
                <div style={{ fontSize: "1.2rem", fontWeight: 800, color: "var(--emerald-400)" }}>
                  {selectedSiteProps.carbon_stored_tons} tons
                </div>
              </div>
              <div style={{ background: "rgba(0,0,0,0.3)", padding: "12px", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Biodiversity Score</span>
                <div style={{ fontSize: "1.2rem", fontWeight: 800, color: "var(--purple-400)" }}>
                  {selectedSiteProps.biodiversity_score} / 100
                </div>
              </div>
              <div style={{ background: "rgba(0,0,0,0.3)", padding: "12px", borderRadius: "8px" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Soil Type</span>
                <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff" }}>
                  {selectedSiteProps.soil_type || "Loam"}
                </div>
              </div>
            </div>

            {/* Time Series Charts */}
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div>
                <h4 style={{ fontSize: "0.85rem", fontWeight: 700, color: "#ffffff", marginBottom: "8px" }}>
                  Carbon Progression Trajectory
                </h4>
                <div style={{ background: "rgba(0,0,0,0.2)", padding: "12px", borderRadius: "8px" }}>
                  <CarbonTrendChart dataPoints={siteAnalytics} />
                </div>
              </div>

              <div>
                <h4 style={{ fontSize: "0.85rem", fontWeight: 700, color: "#ffffff", marginBottom: "8px" }}>
                  Biodiversity Health Score
                </h4>
                <div style={{ background: "rgba(0,0,0,0.2)", padding: "12px", borderRadius: "8px" }}>
                  <BiodiversityChart dataPoints={siteAnalytics} />
                </div>
              </div>
            </div>
          </aside>
        )}
      </div>

      {/* Add Site Modal */}
      <Modal
        isOpen={isAddSiteOpen}
        onClose={() => setIsAddSiteOpen(false)}
        title="Draw & Save Site Boundary (PostGIS)"
        maxWidth="800px"
      >
        <form onSubmit={handleSaveSite}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "16px" }}>
            <div className="input-group">
              <label className="input-label">Attach to Project *</label>
              <select
                className="input-field"
                value={targetProject}
                onChange={(e) => setTargetProject(e.target.value)}
                required
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id} style={{ background: "#0f172a" }}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="input-group">
              <label className="input-label">Site Sector Name *</label>
              <input
                type="text"
                className="input-field"
                placeholder="e.g. Mangrove Tidal Zone 2"
                value={siteName}
                onChange={(e) => setSiteName(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="input-group" style={{ marginBottom: "16px" }}>
            <label className="input-label">Soil Type</label>
            <input
              type="text"
              className="input-field"
              value={soilType}
              onChange={(e) => setSoilType(e.target.value)}
            />
          </div>

          <div style={{ marginBottom: "16px" }}>
            <label className="input-label" style={{ display: "block", marginBottom: "8px" }}>
              Draw Polygon On Map (Live Area Computation) *
            </label>
            <PolygonDrawer
              onPolygonCreated={(geometry, area) => {
                setDrawnGeometry(geometry);
                setDrawnArea(area);
              }}
              height="320px"
            />
          </div>

          <div className="input-group">
            <label className="input-label">Description</label>
            <textarea
              className="input-field"
              placeholder="Ecological notes..."
              value={siteDesc}
              onChange={(e) => setSiteDesc(e.target.value)}
              style={{ minHeight: "50px" }}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "16px" }}>
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
              disabled={saving || !drawnGeometry}
            >
              {saving ? "Saving..." : `Store PostGIS Polygon (${drawnArea} ha)`}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
