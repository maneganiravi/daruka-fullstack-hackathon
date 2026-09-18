import math
from typing import Any, Dict, Tuple
from shapely.geometry import shape


def calculate_polygon_area_hectares(geojson_geometry: Dict[str, Any]) -> float:
    """
    Calculate the geodesic area of a GeoJSON Polygon in hectares.
    Uses spherical polygon area calculation (WGS84).
    1 hectare = 10,000 square meters.
    """
    try:
        geom_type = geojson_geometry.get("type")
        coords = geojson_geometry.get("coordinates")

        if not coords or geom_type not in ["Polygon", "MultiPolygon"]:
            return 0.0

        if geom_type == "Polygon":
            polygon_rings = coords
        else:  # MultiPolygon
            polygon_rings = coords[0]

        # Use spherical excess on the primary exterior ring
        ring = polygon_rings[0]
        if len(ring) < 3:
            return 0.0

        area_sq_meters = 0.0
        r = 6378137.0  # Earth radius in meters (WGS84)

        for i in range(len(ring)):
            p1 = ring[i]
            p2 = ring[(i + 1) % len(ring)]

            lon1, lat1 = math.radians(p1[0]), math.radians(p1[1])
            lon2, lat2 = math.radians(p2[0]), math.radians(p2[1])

            area_sq_meters += (lon2 - lon1) * (2.0 + math.sin(lat1) + math.sin(lat2))

        area_sq_meters = abs(area_sq_meters * (r * r) / 2.0)
        area_hectares = round(area_sq_meters / 10000.0, 2)
        return max(area_hectares, 0.01)

    except Exception:
        try:
            poly = shape(geojson_geometry)
            bounds = poly.bounds
            mid_lat = (bounds[1] + bounds[3]) / 2.0
            lat_scale = 111320.0
            lon_scale = 111320.0 * math.cos(math.radians(mid_lat))
            area_sq_meters = poly.area * lat_scale * lon_scale
            return round(max(area_sq_meters / 10000.0, 0.01), 2)
        except Exception:
            return 1.0


def get_polygon_centroid(geojson_geometry: Dict[str, Any]) -> Tuple[float, float]:
    """
    Calculate the center (latitude, longitude) of a GeoJSON Polygon for map centering.
    Returns (longitude, latitude).
    """
    try:
        poly = shape(geojson_geometry)
        centroid = poly.centroid
        return (round(centroid.x, 6), round(centroid.y, 6))
    except Exception:
        return (0.0, 0.0)
