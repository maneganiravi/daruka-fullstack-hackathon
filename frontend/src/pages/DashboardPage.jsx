import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Navbar } from "../components/common/Navbar";
import { StatCard } from "../components/common/StatCard";
import { MapboxGLView } from "../components/map/MapboxGLView";
import { analyticsService } from "../services/analyticsService";
import { siteService } from "../services/siteService";
import { projectService } from "../services/projectService";
import { useAuth } from "../context/AuthContext";
import {
  Globe,
  Trees,
  Sparkles,
  ArrowUpRight,
  PlusCircle,
  FolderTree,
  Activity,
} from "lucide-react";

export const DashboardPage = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [sitesGeoJSON, setSitesGeoJSON] = useState(null);
  const [recentProjects, setRecentProjects] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashMetrics, geojson, projects] = await Promise.all([
          analyticsService.getDashboardMetrics(),
          siteService.getSitesGeoJSON(),
          projectService.getProjects({ limit: 4 }),
        ]);
        setMetrics(dashMetrics);
        setSitesGeoJSON(geojson);
        setRecentProjects(projects);
      } catch (err) {
        console.error("Dashboard data load error:", err);
      }
    };
    fetchData();
  }, []);

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />

      <main style={{ flex: 1, padding: "32px 24px", maxWidth: "1400px", margin: "0 auto", width: "100%" }}>
        {/* Welcome Banner */}
        <div
          className="glass-panel"
          style={{
            padding: "28px 32px",
            marginBottom: "28px",
            background: "linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(6, 78, 59, 0.4) 100%)",
            border: "1px solid rgba(16, 185, 129, 0.2)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "20px",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--emerald-400)", fontSize: "0.85rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>
              <Sparkles size={16} /> Global Ecological Intelligence Platform
            </div>
            <h1 style={{ fontSize: "1.8rem", fontWeight: 800, color: "#ffffff", marginTop: "6px" }}>
              Welcome back, {user?.full_name || "Environmental Partner"}
            </h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", marginTop: "4px" }}>
              Monitor high-resolution PostGIS project site polygons, blue carbon sinks, and live biodiversity indexes.
            </p>
          </div>

          <div style={{ display: "flex", gap: "12px" }}>
            <Link to="/map" className="btn btn-secondary">
              <Globe size={18} /> Open GIS Workspace
            </Link>
            <Link to="/projects" className="btn btn-primary">
              <PlusCircle size={18} /> Manage Projects
            </Link>
          </div>
        </div>

        {/* Top KPI Metrics Cards Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
            gap: "20px",
            marginBottom: "28px",
          }}
        >
          <StatCard
            title="Total Land Restored"
            value={metrics?.total_area_hectares?.toLocaleString() || "0"}
            unit="hectares"
            subtitle={`${metrics?.total_sites || 0} mapped site polygons`}
            icon={Globe}
            color="emerald"
            trend="14.2%"
          />
          <StatCard
            title="Carbon Sequestered"
            value={metrics?.total_carbon_stored_tons?.toLocaleString() || "0"}
            unit="tons CO₂e"
            subtitle="Calculated soil & biomass capture"
            icon={Trees}
            color="cyan"
            trend="22.5%"
          />
          <StatCard
            title="Average Biodiversity Score"
            value={metrics?.average_biodiversity_score || "0"}
            unit="/ 100"
            subtitle={`${metrics?.total_species_recorded || 0} endemic species logged`}
            icon={Activity}
            color="purple"
            trend="8.1%"
          />
          <StatCard
            title="Active Restoration Projects"
            value={metrics?.active_projects || "0"}
            unit={`of ${metrics?.total_projects || 0}`}
            subtitle="Corridors, mangroves & scrublands"
            icon={FolderTree}
            color="amber"
          />
        </div>

        {/* Main Content: Interactive Map & Recent Projects */}
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "24px", alignItems: "start" }}>
          {/* Mapbox Interactive Overview */}
          <div className="glass-panel" style={{ padding: "20px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
              <div>
                <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff" }}>
                  Global Project Sites Map
                </h3>
                <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  Click on any site boundary to inspect live area and carbon storage
                </p>
              </div>
              <Link to="/map" className="btn btn-sm btn-secondary">
                Fullscreen GIS <ArrowUpRight size={14} />
              </Link>
            </div>

            <MapboxGLView
              sitesGeoJSON={sitesGeoJSON}
              height="480px"
              showControls={true}
            />
          </div>

          {/* Recent Restoration Projects List */}
          <div className="glass-panel" style={{ padding: "24px" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
              <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#ffffff" }}>
                Restoration Projects
              </h3>
              <Link to="/projects" style={{ fontSize: "0.8rem", color: "var(--emerald-400)", fontWeight: 600, textDecoration: "none" }}>
                View All →
              </Link>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {recentProjects.map((p) => (
                <Link
                  key={p.id}
                  to={`/projects/${p.id}`}
                  className="glass-card"
                  style={{
                    padding: "16px",
                    textDecoration: "none",
                    display: "block",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "8px" }}>
                    <h4 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#ffffff", lineHeight: 1.3 }}>
                      {p.name}
                    </h4>
                    <span className={`badge badge-${p.status}`}>
                      {p.status}
                    </span>
                  </div>

                  <p style={{ fontSize: "0.8rem", color: "var(--text-secondary)", margin: "8px 0 12px", lineHeight: 1.4, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                    {p.description || "No project description provided."}
                  </p>

                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", fontSize: "0.75rem", color: "var(--text-muted)", paddingTop: "8px", borderTop: "1px solid var(--border-color)" }}>
                    <span>📍 {p.sites_count || 0} Sites</span>
                    <span>🌿 {p.total_area_hectares || 0} ha</span>
                    <strong style={{ color: "var(--emerald-400)" }}>{p.total_carbon_stored_tons || 0} t CO₂</strong>
                  </div>
                </Link>
              ))}

              {recentProjects.length === 0 && (
                <div style={{ padding: "24px", textAlign: "center", color: "var(--text-muted)" }}>
                  No projects created yet.
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
