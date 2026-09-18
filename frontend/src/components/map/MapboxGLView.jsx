import React, { useEffect, useRef, useState, useCallback } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { Maximize } from "lucide-react";

// Standard Mapbox Style Spec v8 Raster Tiles for high reliability and clean display (no watermarks)
const RASTER_STYLES = {
  satellite: {
    version: 8,
    name: "Satellite",
    sources: {
      "esri-satellite": {
        type: "raster",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        ],
        tileSize: 256,
        attribution: "Tiles &copy; Esri, Maxar, Earthstar Geographics",
        maxzoom: 19,
      },
      "esri-satellite-labels": {
        type: "raster",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        ],
        tileSize: 256,
        maxzoom: 19,
      },
    },
    layers: [
      {
        id: "esri-satellite-layer",
        type: "raster",
        source: "esri-satellite",
        minzoom: 0,
        maxzoom: 22,
      },
      {
        id: "esri-satellite-labels-layer",
        type: "raster",
        source: "esri-satellite-labels",
        minzoom: 0,
        maxzoom: 22,
      },
    ],
  },
  dark: {
    version: 8,
    name: "Dark Vector",
    sources: {
      "esri-dark-base": {
        type: "raster",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
        ],
        tileSize: 256,
        attribution: "Tiles &copy; Esri &copy; OpenStreetMap contributors",
        maxzoom: 16,
      },
      "esri-dark-labels": {
        type: "raster",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}",
        ],
        tileSize: 256,
        maxzoom: 16,
      },
    },
    layers: [
      {
        id: "esri-dark-base-layer",
        type: "raster",
        source: "esri-dark-base",
        minzoom: 0,
        maxzoom: 22,
      },
      {
        id: "esri-dark-labels-layer",
        type: "raster",
        source: "esri-dark-labels",
        minzoom: 0,
        maxzoom: 22,
      },
    ],
  },
  streets: {
    version: 8,
    name: "Terrain & Streets",
    sources: {
      "esri-topo": {
        type: "raster",
        tiles: [
          "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        ],
        tileSize: 256,
        attribution: "Tiles &copy; Esri &copy; National Geographic, DeLorme, HERE",
        maxzoom: 19,
      },
    },
    layers: [
      {
        id: "esri-topo-layer",
        type: "raster",
        source: "esri-topo",
        minzoom: 0,
        maxzoom: 22,
      },
    ],
  },
};

const MAPBOX_HOSTED_STYLES = {
  satellite: "mapbox://styles/mapbox/satellite-streets-v12",
  dark: "mapbox://styles/mapbox/dark-v11",
  streets: "mapbox://styles/mapbox/outdoors-v12",
};

const envToken = (
  import.meta.env.VITE_MAPBOX_ACCESS_TOKEN ||
  import.meta.env.VITE_MAPBOX_TOKEN ||
  ""
).trim();
const hasValidToken = Boolean(envToken && envToken.startsWith("pk.") && envToken.length > 20);

// Set mapboxgl.accessToken for Mapbox GL JS engine
mapboxgl.accessToken =
  envToken ||
  "pk.eyJ1IjoibWFwYm94LWdsLWRlbW8iLCJhIjoiY2x2NHZ6eWlsMDBycjJsbjFjMmpsYnVpNiJ9.demo_token";

export const getMapStyleDefinition = (styleKey = "satellite") => {
  if (hasValidToken) {
    return MAPBOX_HOSTED_STYLES[styleKey] || MAPBOX_HOSTED_STYLES.satellite;
  }
  return RASTER_STYLES[styleKey] || RASTER_STYLES.satellite;
};

const EMPTY_GEOJSON = { type: "FeatureCollection", features: [] };

export const MapboxGLView = ({
  sitesGeoJSON,
  selectedSiteId: _selectedSiteId,
  onSiteClick,
  onMapReady,
  center = [78.9629, 20.5937],
  zoom = 4,
  height = "550px",
  showControls = true,
  interactive = true,
}) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [mapStyle, setMapStyle] = useState("satellite");
  const isLoaded = useRef(false);
  const hasAutoFitted = useRef(false);
  const onSiteClickRef = useRef(onSiteClick);
  useEffect(() => {
    onSiteClickRef.current = onSiteClick;
  }, [onSiteClick]);


  const sourceId = "daruka-sites-source";
  const fillLayerId = "daruka-sites-fill";
  const lineLayerId = "daruka-sites-line";

  // Fit Bounds Helper
  const fitAllBounds = useCallback((customPadding = 60) => {
    if (!map.current || !sitesGeoJSON?.features?.length) return;
    try {
      const bounds = new mapboxgl.LngLatBounds();
      let hasCoords = false;

      sitesGeoJSON.features.forEach((feature) => {
        const geom = feature.geometry;
        if (geom?.type === "Polygon" && Array.isArray(geom.coordinates)) {
          geom.coordinates.forEach((ring) => {
            if (Array.isArray(ring)) {
              ring.forEach((coord) => {
                if (Array.isArray(coord) && coord.length >= 2 && !isNaN(coord[0]) && !isNaN(coord[1])) {
                  bounds.extend(coord);
                  hasCoords = true;
                }
              });
            }
          });
        }
      });

      if (hasCoords && !bounds.isEmpty()) {
        map.current.fitBounds(bounds, { padding: customPadding, maxZoom: 14, duration: 800 });
      }
    } catch (e) {
      console.warn("Could not fit map bounds:", e);
    }
  }, [sitesGeoJSON]);

  // Add or Update GeoJSON Layers safely
  const updateLayers = useCallback(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;

    const currentMap = map.current;
    const geoData = sitesGeoJSON || EMPTY_GEOJSON;

    try {
      if (currentMap.getSource(sourceId)) {
        currentMap.getSource(sourceId).setData(geoData);
      } else {
        currentMap.addSource(sourceId, {
          type: "geojson",
          data: geoData,
        });
      }

      if (!currentMap.getLayer(fillLayerId)) {
        currentMap.addLayer({
          id: fillLayerId,
          type: "fill",
          source: sourceId,
          paint: {
            "fill-color": "#10b981",
            "fill-opacity": 0.45,
          },
        });

        // Click Handler on Polygons
        currentMap.on("click", fillLayerId, (e) => {
          if (e.features && e.features.length > 0) {
            const feature = e.features[0];
            const props = feature.properties;
            if (onSiteClickRef.current) {
              onSiteClickRef.current(props, feature.geometry);
            }

            // Show Popup
            new mapboxgl.Popup({ offset: 15, closeButton: true })
              .setLngLat(e.lngLat)
              .setHTML(`
                <div style="padding: 4px;">
                  <div style="font-size: 0.7rem; text-transform: uppercase; font-weight: 700; color: #34d399; margin-bottom: 2px;">
                    ${props.project_name || "Restoration Project"}
                  </div>
                  <h4 style="font-size: 0.95rem; font-weight: 700; color: #ffffff; margin-bottom: 6px;">
                    📍 ${props.name}
                  </h4>
                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.8rem; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div>
                      <span style="color: #94a3b8;">Area:</span>
                      <strong style="color: #ffffff; display: block;">${Number(props.area_hectares || 0).toFixed(1)} ha</strong>
                    </div>
                    <div>
                      <span style="color: #94a3b8;">Carbon Stored:</span>
                      <strong style="color: #34d399; display: block;">${Number(props.carbon_stored_tons || 0).toFixed(0)} tons</strong>
                    </div>
                  </div>
                </div>
              `)
              .addTo(currentMap);
          }
        });

        // Cursor pointer styling
        currentMap.on("mouseenter", fillLayerId, () => {
          if (map.current) map.current.getCanvas().style.cursor = "pointer";
        });
        currentMap.on("mouseleave", fillLayerId, () => {
          if (map.current) map.current.getCanvas().style.cursor = "";
        });
      }

      if (!currentMap.getLayer(lineLayerId)) {
        currentMap.addLayer({
          id: lineLayerId,
          type: "line",
          source: sourceId,
          paint: {
            "line-color": "#34d399",
            "line-width": 2.5,
          },
        });
      }

      // Auto-fit bounds on initial data arrival
      if (!hasAutoFitted.current && geoData.features && geoData.features.length > 0) {
        hasAutoFitted.current = true;
        fitAllBounds(70);
      }
    } catch (err) {
      console.warn("Layer update notice:", err);
    }
  }, [sitesGeoJSON, fitAllBounds]);

  // Single Mapbox Instance Lifecycle: Mount ONCE
  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    try {
      const mapInstance = new mapboxgl.Map({
        container: mapContainer.current,
        style: getMapStyleDefinition(mapStyle),
        center: center,
        zoom: zoom,
        attributionControl: true,
        interactive: interactive,
        preserveDrawingBuffer: true,
        transformRequest: (url) => {
          if (!hasValidToken && (url.includes("api.mapbox.com/map-sessions") || url.includes("events.mapbox.com"))) {
            return { url: "data:application/json;base64,e30=" };
          }
          return { url };
        },
      });

      map.current = mapInstance;
      window.__debug_map = mapInstance;

      mapInstance.on("load", () => {
        isLoaded.current = true;
        mapInstance.resize();
        updateLayers();
        if (onMapReady) onMapReady(mapInstance);
      });

      mapInstance.on("error", (e) => {
        if (e && e.error) {
          console.warn("Mapbox notification:", e.error?.message || e);
        }
      });

      // Navigation controls
      if (showControls) {
        mapInstance.addControl(new mapboxgl.NavigationControl({ showCompass: true }), "top-right");
      }

      // Responsive Resize Handling
      const handleResize = () => {
        if (map.current) map.current.resize();
      };
      window.addEventListener("resize", handleResize);

      const resizeObserver = new ResizeObserver(() => {
        if (map.current) {
          map.current.resize();
        }
      });

      if (mapContainer.current) {
        resizeObserver.observe(mapContainer.current);
      }

      const t1 = setTimeout(handleResize, 100);
      const t2 = setTimeout(handleResize, 500);

      return () => {
        clearTimeout(t1);
        clearTimeout(t2);
        window.removeEventListener("resize", handleResize);
        resizeObserver.disconnect();
        if (map.current) {
          map.current.remove();
          map.current = null;
          isLoaded.current = false;
        }
      };
    } catch (err) {
      console.error("Failed to initialize Mapbox GL:", err);
    }
  }, []);

  // Update existing layers whenever sitesGeoJSON data changes
  useEffect(() => {
    if (!map.current || !isLoaded.current) return;

    if (map.current.isStyleLoaded()) {
      updateLayers();
    } else {
      map.current.once("style.load", updateLayers);
    }
  }, [sitesGeoJSON, updateLayers]);

  // Update Style on Toggle without destroying the map instance
  const changeStyle = (newStyle) => {
    if (!map.current || newStyle === mapStyle) return;
    setMapStyle(newStyle);
    map.current.setStyle(getMapStyleDefinition(newStyle));
    map.current.once("style.load", () => {
      updateLayers();
    });
  };

  return (
    <div style={{ position: "relative", width: "100%", height, minHeight: "350px", borderRadius: "var(--radius-lg)", overflow: "hidden", border: "1px solid var(--border-color)", background: "#0a0f1d" }}>
      {/* Mapbox Canvas Container */}
      <div ref={mapContainer} style={{ width: "100%", height: "100%", position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }} />

      {/* Floating Layer & Style Controls */}
      {showControls && (
        <div
          style={{
            position: "absolute",
            top: "16px",
            left: "16px",
            zIndex: 10,
            display: "flex",
            alignItems: "center",
            gap: "8px",
            background: "rgba(15, 23, 42, 0.85)",
            backdropFilter: "blur(12px)",
            padding: "6px 8px",
            borderRadius: "var(--radius-sm)",
            border: "1px solid var(--border-color)",
          }}
        >
          <button
            type="button"
            onClick={() => changeStyle("satellite")}
            className="btn btn-sm"
            style={{
              padding: "4px 10px",
              background: mapStyle === "satellite" ? "var(--emerald-600)" : "transparent",
              color: mapStyle === "satellite" ? "#ffffff" : "var(--text-secondary)",
              border: "none",
            }}
          >
            Satellite
          </button>
          <button
            type="button"
            onClick={() => changeStyle("dark")}
            className="btn btn-sm"
            style={{
              padding: "4px 10px",
              background: mapStyle === "dark" ? "var(--emerald-600)" : "transparent",
              color: mapStyle === "dark" ? "#ffffff" : "var(--text-secondary)",
              border: "none",
            }}
          >
            Dark Vector
          </button>
          <button
            type="button"
            onClick={() => changeStyle("streets")}
            className="btn btn-sm"
            style={{
              padding: "4px 10px",
              background: mapStyle === "streets" ? "var(--emerald-600)" : "transparent",
              color: mapStyle === "streets" ? "#ffffff" : "var(--text-secondary)",
              border: "none",
            }}
          >
            Terrain
          </button>

          <div style={{ width: "1px", height: "18px", background: "var(--border-color)", margin: "0 4px" }} />

          <button
            type="button"
            onClick={() => fitAllBounds(60)}
            className="btn btn-sm btn-secondary"
            style={{ padding: "4px 8px" }}
            title="Fit All Sites"
          >
            <Maximize size={14} /> Fit All
          </button>
        </div>
      )}
    </div>
  );
};
