import React, { useEffect, useRef, useState, useCallback } from "react";
import mapboxgl from "mapbox-gl";
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import "mapbox-gl/dist/mapbox-gl.css";
import "@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css";
import { PenTool, Trash2, AlertCircle } from "lucide-react";
import { getMapStyleDefinition } from "./MapboxGLView";

export const PolygonDrawer = ({ onPolygonCreated, initialCenter = [76.10, 11.67], height = "340px" }) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const draw = useRef(null);
  const [areaHectares, setAreaHectares] = useState(0.0);
  const [hasPolygon, setHasPolygon] = useState(false);
  const [isDrawing, setIsDrawing] = useState(false);

  const updateArea = useCallback(() => {
    if (!draw.current) return;
    const data = draw.current.getAll();
    if (data.features && data.features.length > 0) {
      const feature = data.features[data.features.length - 1];
      if (feature.geometry && feature.geometry.type === "Polygon") {
        const coords = feature.geometry.coordinates[0];
        // Calculate spherical geodesic area
        let area = 0.0;
        const r = 6378137.0; // Earth mean radius in meters
        if (coords && coords.length > 2) {
          for (let i = 0; i < coords.length - 1; i++) {
            const p1 = coords[i];
            const p2 = coords[i + 1];
            const lon1 = (p1[0] * Math.PI) / 180.0;
            const lat1 = (p1[1] * Math.PI) / 180.0;
            const lon2 = (p2[0] * Math.PI) / 180.0;
            const lat2 = (p2[1] * Math.PI) / 180.0;
            area += (lon2 - lon1) * (2 + Math.sin(lat1) + Math.sin(lat2));
          }
          area = Math.abs((area * r * r) / 2.0);
          const ha = parseFloat((area / 10000.0).toFixed(2));
          setAreaHectares(ha);
          setHasPolygon(true);
          setIsDrawing(false);
          if (onPolygonCreated) {
            onPolygonCreated(feature.geometry, ha);
          }
          return;
        }
      }
    }

    setHasPolygon(false);
    setAreaHectares(0.0);
    if (onPolygonCreated) {
      onPolygonCreated(null, 0.0);
    }
  }, [onPolygonCreated]);

  // Initialize Map & MapboxDraw
  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    try {
      const mapInstance = new mapboxgl.Map({
        container: mapContainer.current,
        style: getMapStyleDefinition("satellite"),
        center: initialCenter,
        zoom: 12,
        attributionControl: true,
        preserveDrawingBuffer: true,
        transformRequest: (url) => {
          if (url.includes("api.mapbox.com/map-sessions") || url.includes("events.mapbox.com")) {
            return { url: "data:application/json;base64,e30=" };
          }
          return { url };
        },
      });

      map.current = mapInstance;

      const drawTool = new MapboxDraw({
        displayControlsDefault: false,
        controls: {},
        defaultMode: "draw_polygon",
      });

      draw.current = drawTool;
      mapInstance.addControl(drawTool, "top-left");
      setIsDrawing(true);

      const handleResize = () => {
        if (map.current) map.current.resize();
      };

      mapInstance.on("load", () => {
        handleResize();
      });

      mapInstance.on("draw.create", updateArea);
      mapInstance.on("draw.delete", updateArea);
      mapInstance.on("draw.update", updateArea);
      mapInstance.on("draw.modechange", (e) => {
        setIsDrawing(e.mode === "draw_polygon");
      });

      window.addEventListener("resize", handleResize);

      const resizeObserver = new ResizeObserver(() => {
        handleResize();
      });

      if (mapContainer.current) {
        resizeObserver.observe(mapContainer.current);
      }

      // Delayed resizes for modal transition animations
      const t1 = setTimeout(handleResize, 100);
      const t2 = setTimeout(handleResize, 350);
      const t3 = setTimeout(handleResize, 700);

      return () => {
        clearTimeout(t1);
        clearTimeout(t2);
        clearTimeout(t3);
        window.removeEventListener("resize", handleResize);
        resizeObserver.disconnect();
        if (map.current) {
          map.current.remove();
          map.current = null;
        }
      };
    } catch (e) {
      console.error("MapboxDraw initialization error:", e);
    }
  }, [initialCenter, updateArea]);

  const handleStartDraw = (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (draw.current) {
      draw.current.deleteAll();
      draw.current.changeMode("draw_polygon");
      setHasPolygon(false);
      setIsDrawing(true);
      setAreaHectares(0.0);
      if (onPolygonCreated) onPolygonCreated(null, 0.0);
    }
  };

  const handleClear = (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (draw.current) {
      draw.current.deleteAll();
      setHasPolygon(false);
      setIsDrawing(false);
      setAreaHectares(0.0);
      if (onPolygonCreated) onPolygonCreated(null, 0.0);
    }
  };

  return (
    <div style={{ position: "relative", width: "100%", height, minHeight: "300px", borderRadius: "var(--radius-md)", overflow: "hidden", border: "1px solid var(--border-color)", background: "#0a0f1d" }}>
      {/* Map Container */}
      <div ref={mapContainer} style={{ width: "100%", height: "100%", position: "absolute", top: 0, left: 0, right: 0, bottom: 0, cursor: isDrawing ? "crosshair" : "default" }} />

      {/* Floating Instructions & Area Badge */}
      <div
        onClick={(e) => e.stopPropagation()}
        onMouseDown={(e) => e.stopPropagation()}
        style={{
          position: "absolute",
          top: "12px",
          right: "12px",
          zIndex: 10,
          background: "rgba(15, 23, 42, 0.92)",
          backdropFilter: "blur(14px)",
          padding: "12px 16px",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-color)",
          boxShadow: "0 8px 32px rgba(0,0,0,0.5)",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          minWidth: "240px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)", fontWeight: 600 }}>
            Calculated Area:
          </span>
          <strong style={{ fontSize: "1.15rem", color: "var(--emerald-400)", fontWeight: 800 }}>
            {areaHectares} ha
          </strong>
        </div>

        <div style={{ display: "flex", gap: "8px" }}>
          <button
            type="button"
            onClick={handleStartDraw}
            className="btn btn-sm"
            style={{
              flex: 1,
              padding: "7px 12px",
              fontSize: "0.8rem",
              background: isDrawing ? "linear-gradient(135deg, #10b981 0%, #059669 100%)" : "rgba(16, 185, 129, 0.2)",
              color: "#ffffff",
              border: "1px solid rgba(16, 185, 129, 0.4)",
              boxShadow: isDrawing ? "0 0 15px rgba(16, 185, 129, 0.4)" : "none",
            }}
          >
            <PenTool size={14} /> {isDrawing ? "Drawing Active" : "Draw Boundary"}
          </button>
          <button
            type="button"
            onClick={handleClear}
            className="btn btn-sm btn-secondary"
            style={{ padding: "7px 10px" }}
            title="Clear Drawing"
          >
            <Trash2 size={14} />
          </button>
        </div>

        {isDrawing && !hasPolygon && (
          <div style={{ fontSize: "0.75rem", color: "#34d399", display: "flex", alignItems: "center", gap: "6px", background: "rgba(16, 185, 129, 0.1)", padding: "6px 8px", borderRadius: "4px", border: "1px solid rgba(16, 185, 129, 0.2)" }}>
            <AlertCircle size={13} color="#34d399" /> Click points on map to draw. Double-click to close.
          </div>
        )}
      </div>
    </div>
  );
};
