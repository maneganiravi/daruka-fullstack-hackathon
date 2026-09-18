import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { UserPlus, ShieldAlert } from "lucide-react";
import { getErrorMessage } from "../services/api";

export const RegisterPage = () => {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("user");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({
        full_name: fullName,
        email,
        password,
        role,
      });
      navigate("/");
    } catch (err) {
      setError(getErrorMessage(err, "Registration failed. Please check your inputs."));
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
          maxWidth: "480px",
          padding: "36px",
          boxShadow: "var(--shadow-lg)",
        }}
      >
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
            Create Your Account
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: "6px" }}>
            Join the global ecological monitoring network
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

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label">Full Name</label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. Dr. Maya Sharma"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>

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
              placeholder="At least 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          <div className="input-group">
            <label className="input-label">Account Role</label>
            <select
              className="input-field"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              style={{ cursor: "pointer" }}
            >
              <option value="user" style={{ background: "#0f172a" }}>
                Ecologist / Project Member (Standard)
              </option>
              <option value="admin" style={{ background: "#0f172a" }}>
                Administrator / Executive (Full Control)
              </option>
            </select>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: "100%", marginTop: "16px", padding: "12px" }}
            disabled={loading}
          >
            <UserPlus size={18} />
            {loading ? "Creating Account..." : "Register & Start Mapping"}
          </button>
        </form>

        <div style={{ textAlign: "center", marginTop: "24px", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "var(--emerald-400)", fontWeight: 700, textDecoration: "none" }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
