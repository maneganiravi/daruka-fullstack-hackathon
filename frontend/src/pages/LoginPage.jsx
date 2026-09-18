import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogIn, Leaf, ShieldAlert, CheckCircle2, ArrowRight } from "lucide-react";
import { getErrorMessage } from "../services/api";

export const LoginPage = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(getErrorMessage(err, "Invalid email or password. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError("");
    setLoading(true);
    try {
      await login(demoEmail, demoPassword);
      navigate("/");
    } catch (err) {
      setError(getErrorMessage(err, "Demo login failed. Make sure backend is running."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
      }}
    >
      <div
        className="glass-panel"
        style={{
          width: "100%",
          maxWidth: "460px",
          padding: "36px",
          boxShadow: "var(--shadow-lg)",
        }}
      >
        {/* Brand Header */}
        <div style={{ textAlign: "center", marginBottom: "28px" }}>
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "16px",
              background: "linear-gradient(135deg, #10b981 0%, #06b6d4 100%)",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "28px",
              marginBottom: "16px",
              boxShadow: "0 8px 24px rgba(16, 185, 129, 0.4)",
            }}
          >
            🌱
          </div>
          <h2 style={{ fontSize: "1.6rem", fontWeight: 800, color: "#ffffff", letterSpacing: "-0.02em" }}>
            Welcome to Darukaa<span style={{ color: "var(--emerald-400)" }}>.Earth</span>
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: "6px" }}>
            Geospatial Land Restoration & PostGIS Carbon GIS
          </p>
        </div>

        {error && (
          <div
            style={{
              padding: "12px 16px",
              background: "rgba(244, 63, 94, 0.15)",
              border: "1px solid rgba(244, 63, 94, 0.3)",
              borderRadius: "var(--radius-sm)",
              color: "#fb7185",
              fontSize: "0.85rem",
              marginBottom: "20px",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <ShieldAlert size={18} />
            {error}
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label">Email Address</label>
            <input
              type="email"
              className="input-field"
              placeholder="name@organization.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label">Password</label>
            <input
              type="password"
              className="input-field"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: "100%", marginTop: "12px", padding: "12px" }}
            disabled={loading}
          >
            <LogIn size={18} />
            {loading ? "Authenticating..." : "Sign In to Platform"}
          </button>
        </form>

        {/* 1-Click Demo Evaluation Credentials */}
        <div style={{ marginTop: "24px", paddingTop: "20px", borderTop: "1px solid var(--border-color)" }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: "12px", textAlign: "center" }}>
            Hackathon 1-Click Demo Logins
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
            <button
              type="button"
              onClick={() => handleDemoLogin("admin@darukaa.earth", "AdminPassword123!")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "0.78rem", padding: "8px" }}
            >
              👑 Admin Demo
            </button>
            <button
              type="button"
              onClick={() => handleDemoLogin("ecologist@darukaa.earth", "Ecologist2026!")}
              className="btn btn-secondary btn-sm"
              style={{ fontSize: "0.78rem", padding: "8px" }}
            >
              🌿 Ecologist Demo
            </button>
          </div>
        </div>

        {/* Register Link */}
        <div style={{ textAlign: "center", marginTop: "24px", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
          Don't have an account yet?{" "}
          <Link to="/register" style={{ color: "var(--emerald-400)", fontWeight: 700, textDecoration: "none" }}>
            Register Now
          </Link>
        </div>
      </div>
    </div>
  );
};
