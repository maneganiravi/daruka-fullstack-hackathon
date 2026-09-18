import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { Navbar } from "../components/common/Navbar";
import { Modal } from "../components/common/Modal";
import { projectService } from "../services/projectService";
import { Plus, Search, ArrowRight } from "lucide-react";

export const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  // Create Project Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newClient, setNewClient] = useState("");
  const [newStatus, setNewStatus] = useState("active");
  const [newTargetCarbon, setNewTargetCarbon] = useState("");
  const [creating, setCreating] = useState(false);

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (statusFilter !== "all") params.status = statusFilter;
      if (search.trim()) params.search = search.trim();

      const data = await projectService.getProjects(params);
      setProjects(data);
    } catch (err) {
      console.error("Failed to load projects:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, search]);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!newName.trim()) return;

    setCreating(true);
    try {
      await projectService.createProject({
        name: newName,
        description: newDesc,
        client_name: newClient,
        status: newStatus,
        target_carbon_sequestration_tons: parseFloat(newTargetCarbon) || 0.0,
      });
      setIsModalOpen(false);
      setNewName("");
      setNewDesc("");
      setNewClient("");
      setNewTargetCarbon("");
      fetchProjects();
    } catch (err) {
      console.error("Error creating project:", err);
      alert("Failed to create project. Please check backend connection.");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar />

      <main style={{ flex: 1, padding: "32px 24px", maxWidth: "1400px", margin: "0 auto", width: "100%" }}>
        {/* Header Title & Actions */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "16px", marginBottom: "28px" }}>
          <div>
            <h1 style={{ fontSize: "1.8rem", fontWeight: 800, color: "#ffffff" }}>
              Restoration Projects
            </h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
              Explore and manage regional ecosystem restoration and carbon projects.
            </p>
          </div>

          <button
            onClick={() => setIsModalOpen(true)}
            className="btn btn-primary"
          >
            <Plus size={18} /> Create New Project
          </button>
        </div>

        {/* Search & Filter Toolbar */}
        <div
          className="glass-panel"
          style={{
            padding: "16px 20px",
            marginBottom: "28px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: "16px",
          }}
        >
          {/* Search Input */}
          <div style={{ position: "relative", minWidth: "280px", flex: "1 1 300px" }}>
            <Search size={18} color="var(--text-muted)" style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)" }} />
            <input
              type="text"
              placeholder="Search projects by name or partner organization..."
              className="input-field"
              style={{ paddingLeft: "38px" }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* Filter Pills */}
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            {["all", "active", "planning", "completed"].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className="btn btn-sm"
                style={{
                  textTransform: "capitalize",
                  background: statusFilter === st ? "var(--emerald-600)" : "var(--bg-tertiary)",
                  color: statusFilter === st ? "#ffffff" : "var(--text-secondary)",
                  border: "1px solid var(--border-color)",
                }}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        {/* Projects Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))",
            gap: "24px",
          }}
        >
          {projects.map((project) => (
            <div
              key={project.id}
              className="glass-card"
              style={{
                padding: "24px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
              }}
            >
              <div>
                <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "8px" }}>
                  <span className={`badge badge-${project.status}`}>
                    {project.status}
                  </span>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    {new Date(project.created_at).toLocaleDateString()}
                  </span>
                </div>

                <h3 style={{ fontSize: "1.2rem", fontWeight: 700, color: "#ffffff", marginTop: "12px", lineHeight: 1.3 }}>
                  {project.name}
                </h3>

                {project.client_name && (
                  <div style={{ fontSize: "0.8rem", color: "var(--emerald-400)", fontWeight: 600, marginTop: "4px" }}>
                    🏢 {project.client_name}
                  </div>
                )}

                <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginTop: "10px", lineHeight: 1.5, minHeight: "50px" }}>
                  {project.description || "No project description available."}
                </p>
              </div>

              <div style={{ marginTop: "20px", paddingTop: "16px", borderTop: "1px solid var(--border-color)" }}>
                {/* Stats Summary */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px", marginBottom: "16px", textAlign: "center" }}>
                  <div style={{ background: "rgba(0,0,0,0.2)", padding: "8px", borderRadius: "8px" }}>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Sites</div>
                    <strong style={{ fontSize: "1rem", color: "#ffffff" }}>{project.sites_count || 0}</strong>
                  </div>
                  <div style={{ background: "rgba(0,0,0,0.2)", padding: "8px", borderRadius: "8px" }}>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Area</div>
                    <strong style={{ fontSize: "1rem", color: "var(--emerald-400)" }}>{project.total_area_hectares || 0} ha</strong>
                  </div>
                  <div style={{ background: "rgba(0,0,0,0.2)", padding: "8px", borderRadius: "8px" }}>
                    <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>Stored</div>
                    <strong style={{ fontSize: "1rem", color: "var(--cyan-400)" }}>{project.total_carbon_stored_tons || 0} t</strong>
                  </div>
                </div>

                <div style={{ display: "flex", gap: "8px" }}>
                  <Link
                    to={`/projects/${project.id}`}
                    className="btn btn-secondary"
                    style={{ flex: 1, fontSize: "0.85rem" }}
                  >
                    View Sites & Analytics <ArrowRight size={14} />
                  </Link>
                </div>
              </div>
            </div>
          ))}

          {projects.length === 0 && !loading && (
            <div style={{ gridColumn: "1 / -1", padding: "60px 20px", textAlign: "center", color: "var(--text-muted)" }}>
              No projects match your search criteria.
            </div>
          )}
        </div>
      </main>

      {/* Create Project Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Restoration Project"
      >
        <form onSubmit={handleCreateProject}>
          <div className="input-group">
            <label className="input-label">Project Name *</label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. Western Ghats Corridor Restoration"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label">Client / Partner Organization</label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. Global Biodiversity Trust"
              value={newClient}
              onChange={(e) => setNewClient(e.target.value)}
            />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div className="input-group">
              <label className="input-label">Initial Status</label>
              <select
                className="input-field"
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
              >
                <option value="active" style={{ background: "#0f172a" }}>Active</option>
                <option value="planning" style={{ background: "#0f172a" }}>Planning</option>
                <option value="completed" style={{ background: "#0f172a" }}>Completed</option>
              </select>
            </div>

            <div className="input-group">
              <label className="input-label">Target Carbon Sequestration (Tons)</label>
              <input
                type="number"
                className="input-field"
                placeholder="e.g. 25000"
                value={newTargetCarbon}
                onChange={(e) => setNewTargetCarbon(e.target.value)}
              />
            </div>
          </div>

          <div className="input-group">
            <label className="input-label">Description & Ecological Objectives</label>
            <textarea
              className="input-field"
              placeholder="Describe the ecosystem, target wildlife species, and afforestation strategies..."
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "24px" }}>
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={creating}
            >
              {creating ? "Creating..." : "Save Project"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
