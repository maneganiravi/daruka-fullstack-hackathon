import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export const CarbonTrendChart = ({ dataPoints, title = "Carbon Sequestration Trajectory" }) => {
  if (!dataPoints || dataPoints.length === 0) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
        No time-series carbon data available for this site yet.
      </div>
    );
  }

  const labels = dataPoints.map((d) => d.record_date);
  const carbonStored = dataPoints.map((d) => d.carbon_stored_tons);
  const carbonRate = dataPoints.map((d) => d.carbon_rate_per_year);

  const chartData = {
    labels,
    datasets: [
      {
        label: "Total Carbon Stored (Tons)",
        data: carbonStored,
        borderColor: "#10b981",
        backgroundColor: "rgba(16, 185, 129, 0.15)",
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointBackgroundColor: "#34d399",
        pointBorderColor: "#ffffff",
        pointRadius: 4,
        pointHoverRadius: 7,
        yAxisID: "y",
      },
      {
        label: "Sequestration Rate (Tons/Yr)",
        data: carbonRate,
        borderColor: "#06b6d4",
        backgroundColor: "transparent",
        borderDash: [5, 5],
        tension: 0.4,
        borderWidth: 2,
        pointBackgroundColor: "#22d3ee",
        pointRadius: 3,
        yAxisID: "y1",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: "index",
      intersect: false,
    },
    plugins: {
      legend: {
        position: "top",
        labels: {
          color: "#94a3b8",
          font: { family: "Plus Jakarta Sans", size: 12, weight: 600 },
          usePointStyle: true,
          pointStyle: "circle",
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: "rgba(15, 23, 42, 0.95)",
        titleColor: "#ffffff",
        bodyColor: "#f8fafc",
        borderColor: "rgba(16, 185, 129, 0.3)",
        borderWidth: 1,
        padding: 12,
        boxPadding: 6,
        usePointStyle: true,
      },
    },
    scales: {
      x: {
        grid: { color: "rgba(255, 255, 255, 0.05)" },
        ticks: { color: "#64748b", font: { family: "Plus Jakarta Sans", size: 11 } },
      },
      y: {
        type: "linear",
        display: true,
        position: "left",
        grid: { color: "rgba(255, 255, 255, 0.06)" },
        ticks: {
          color: "#10b981",
          font: { family: "Plus Jakarta Sans", size: 11 },
          callback: (value) => `${value} t`,
        },
        title: {
          display: true,
          text: "Total Stored (Tons CO₂e)",
          color: "#10b981",
          font: { size: 11, weight: 600 },
        },
      },
      y1: {
        type: "linear",
        display: true,
        position: "right",
        grid: { drawOnChartArea: false },
        ticks: {
          color: "#06b6d4",
          font: { family: "Plus Jakarta Sans", size: 11 },
          callback: (value) => `${value} t/y`,
        },
        title: {
          display: true,
          text: "Rate (t/yr)",
          color: "#06b6d4",
          font: { size: 11, weight: 600 },
        },
      },
    },
  };

  return (
    <div style={{ width: "100%", height: "320px" }}>
      <Line data={chartData} options={options} />
    </div>
  );
};
