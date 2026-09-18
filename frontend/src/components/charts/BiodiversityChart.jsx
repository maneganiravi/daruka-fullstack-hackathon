import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Chart } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export const BiodiversityChart = ({ dataPoints }) => {
  if (!dataPoints || dataPoints.length === 0) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>
        No biodiversity records logged for this site.
      </div>
    );
  }

  const labels = dataPoints.map((d) => d.record_date);
  const bioScore = dataPoints.map((d) => d.biodiversity_score);
  const canopyCover = dataPoints.map((d) => d.canopy_cover_percentage);
  const speciesCount = dataPoints.map((d) => d.species_richness_count);

  const chartData = {
    labels,
    datasets: [
      {
        type: "line",
        label: "Biodiversity Score (0-100)",
        data: bioScore,
        borderColor: "#c084fc",
        backgroundColor: "rgba(192, 132, 252, 0.2)",
        tension: 0.3,
        borderWidth: 3,
        pointBackgroundColor: "#d8b4fe",
        yAxisID: "y",
      },
      {
        type: "line",
        label: "Canopy Cover (%)",
        data: canopyCover,
        borderColor: "#34d399",
        backgroundColor: "rgba(52, 211, 153, 0.1)",
        tension: 0.3,
        borderWidth: 2,
        pointBackgroundColor: "#34d399",
        yAxisID: "y",
      },
      {
        type: "bar",
        label: "Species Richness (Count)",
        data: speciesCount,
        backgroundColor: "rgba(251, 191, 36, 0.4)",
        borderColor: "#fbbf24",
        borderWidth: 1,
        borderRadius: 4,
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
          padding: 16,
        },
      },
      tooltip: {
        backgroundColor: "rgba(15, 23, 42, 0.95)",
        titleColor: "#ffffff",
        bodyColor: "#f8fafc",
        borderColor: "rgba(192, 132, 252, 0.3)",
        borderWidth: 1,
        padding: 12,
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
        max: 100,
        min: 0,
        grid: { color: "rgba(255, 255, 255, 0.06)" },
        ticks: {
          color: "#c084fc",
          font: { family: "Plus Jakarta Sans", size: 11 },
          callback: (v) => `${v}%`,
        },
        title: {
          display: true,
          text: "Health & Cover %",
          color: "#c084fc",
          font: { size: 11, weight: 600 },
        },
      },
      y1: {
        type: "linear",
        display: true,
        position: "right",
        grid: { drawOnChartArea: false },
        ticks: {
          color: "#fbbf24",
          font: { family: "Plus Jakarta Sans", size: 11 },
        },
        title: {
          display: true,
          text: "Species Monitored",
          color: "#fbbf24",
          font: { size: 11, weight: 600 },
        },
      },
    },
  };

  return (
    <div style={{ width: "100%", height: "320px" }}>
      <Chart type="bar" data={chartData} options={options} />
    </div>
  );
};
