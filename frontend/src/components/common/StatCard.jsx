import React from "react";

export const StatCard = ({ title, value, unit, subtitle, icon: Icon, color = "emerald", trend }) => {
  const colorMap = {
    emerald: {
      bg: "rgba(16, 185, 129, 0.12)",
      border: "rgba(16, 185, 129, 0.25)",
      text: "#34d399",
      glow: "0 0 20px rgba(16, 185, 129, 0.15)",
    },
    cyan: {
      bg: "rgba(6, 182, 212, 0.12)",
      border: "rgba(6, 182, 212, 0.25)",
      text: "#22d3ee",
      glow: "0 0 20px rgba(6, 182, 212, 0.15)",
    },
    amber: {
      bg: "rgba(245, 158, 11, 0.12)",
      border: "rgba(245, 158, 11, 0.25)",
      text: "#fbbf24",
      glow: "0 0 20px rgba(245, 158, 11, 0.15)",
    },
    purple: {
      bg: "rgba(192, 132, 252, 0.12)",
      border: "rgba(192, 132, 252, 0.25)",
      text: "#d8b4fe",
      glow: "0 0 20px rgba(192, 132, 252, 0.15)",
    },
  };

  const scheme = colorMap[color] || colorMap.emerald;

  return (
    <div
      className="glass-card"
      style={{
        padding: "20px 24px",
        display: "flex",
        flexDirection: "column",
        gap: "12px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)" }}>
          {title}
        </span>
        {Icon && (
          <div
            style={{
              width: "42px",
              height: "42px",
              borderRadius: "10px",
              background: scheme.bg,
              border: `1px solid ${scheme.border}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: scheme.text,
              boxShadow: scheme.glow,
            }}
          >
            <Icon size={22} />
          </div>
        )}
      </div>

      <div>
        <div style={{ display: "flex", alignItems: "baseline", gap: "6px" }}>
          <span style={{ fontSize: "1.9rem", fontWeight: 800, color: "#ffffff", letterSpacing: "-0.02em" }}>
            {value}
          </span>
          {unit && (
            <span style={{ fontSize: "0.9rem", fontWeight: 600, color: scheme.text }}>
              {unit}
            </span>
          )}
        </div>
        {subtitle && (
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
            {subtitle}
          </div>
        )}
      </div>

      {trend && (
        <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--emerald-400)", display: "flex", alignItems: "center", gap: "4px" }}>
          <span>↑ {trend}</span> vs baseline
        </div>
      )}
    </div>
  );
};
