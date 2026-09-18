import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { 
  Globe, 
  FolderTree, 
  LayoutDashboard, 
  LogOut, 
  ShieldCheck, 
} from "lucide-react";

export const Navbar = () => {
  const { user, isAdmin, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const navLinks = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Projects", path: "/projects", icon: FolderTree },
    { name: "GIS Map Explorer", path: "/map", icon: Globe },
  ];

  return (
    <header className="navbar-container" style={{
      position: "sticky",
      top: 0,
      zIndex: 50,
      backgroundColor: "rgba(10, 15, 29, 0.85)",
      backdropFilter: "blur(16px)",
      WebkitBackdropFilter: "blur(16px)",
      borderBottom: "1px solid var(--border-color)",
      padding: "0 24px",
      height: "70px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between"
    }}>
      {/* Brand Logo */}
      <Link to="/" style={{ display: "flex", alignItems: "center", gap: "12px", textDecoration: "none" }}>
        <div style={{
          width: "40px",
          height: "40px",
          borderRadius: "12px",
          background: "linear-gradient(135deg, #10b981 0%, #06b6d4 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 4px 16px rgba(16, 185, 129, 0.4)"
        }}>
          <span style={{ fontSize: "22px" }}>🌱</span>
        </div>
        <div>
          <div style={{ 
            fontSize: "1.25rem", 
            fontWeight: 800, 
            color: "#ffffff", 
            letterSpacing: "-0.02em",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}>
            Darukaa<span style={{ color: "var(--emerald-400)" }}>.Earth</span>
          </div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", fontWeight: 500 }}>
            Geospatial Carbon & PostGIS GIS
          </div>
        </div>
      </Link>

      {/* Navigation Links */}
      <nav style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        {navLinks.map((link) => {
          const Icon = link.icon;
          const isActive = location.pathname === link.path;
          return (
            <Link
              key={link.path}
              to={link.path}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "8px 16px",
                borderRadius: "var(--radius-sm)",
                fontSize: "0.9rem",
                fontWeight: 600,
                textDecoration: "none",
                color: isActive ? "#ffffff" : "var(--text-secondary)",
                backgroundColor: isActive ? "rgba(16, 185, 129, 0.15)" : "transparent",
                border: isActive ? "1px solid rgba(16, 185, 129, 0.3)" : "1px solid transparent",
                transition: "all 0.2s ease",
              }}
            >
              <Icon size={18} color={isActive ? "var(--emerald-400)" : "currentColor"} />
              {link.name}
            </Link>
          );
        })}
      </nav>

      {/* User Info & Actions */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        {user && (
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "#ffffff", display: "flex", alignItems: "center", gap: "6px", justifyContent: "flex-end" }}>
                {user.full_name || user.email.split("@")[0]}
                {isAdmin && (
                  <span className="badge badge-admin" style={{ padding: "2px 6px", fontSize: "0.65rem" }}>
                    <ShieldCheck size={12} /> Admin
                  </span>
                )}
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{user.email}</div>
            </div>

            <button
              onClick={handleLogout}
              className="btn btn-secondary btn-sm"
              title="Sign Out"
              style={{ padding: "8px", borderRadius: "8px" }}
            >
              <LogOut size={16} />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};
