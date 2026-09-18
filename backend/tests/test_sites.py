def test_site_polygon_lifecycle(client, auth_headers):
    # 1. Create a project first
    proj_res = client.post(
        "/api/projects",
        json={"name": "Sundarbans Afforestation", "description": "Mangrove restoration"},
        headers=auth_headers,
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # 2. Create a site with a valid GeoJSON Polygon
    test_polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [88.80, 21.90],
                [88.85, 21.90],
                [88.85, 21.85],
                [88.80, 21.85],
                [88.80, 21.90],
            ]
        ],
    }
    site_payload = {
        "project_id": project_id,
        "name": "Sundarbans Sector Alpha",
        "description": "Dense tidal mangrove plot",
        "geometry": test_polygon,
        "soil_type": "Saline Alluvial Silt",
        "elevation_meters": 2.0,
    }
    create_site_res = client.post("/api/sites", json=site_payload, headers=auth_headers)
    assert create_site_res.status_code == 201
    site_data = create_site_res.json()
    site_id = site_data["id"]
    assert site_data["name"] == "Sundarbans Sector Alpha"
    assert site_data["area_hectares"] > 0.0
    assert site_data["geometry"]["type"] == "Polygon"

    # 3. Retrieve GeoJSON FeatureCollection
    geojson_res = client.get("/api/sites/geojson", headers=auth_headers)
    assert geojson_res.status_code == 200
    geojson_data = geojson_res.json()
    assert geojson_data["type"] == "FeatureCollection"
    assert len(geojson_data["features"]) >= 1
    feature = next((f for f in geojson_data["features"] if f["id"] == site_id), None)
    assert feature is not None
    assert feature["properties"]["name"] == "Sundarbans Sector Alpha"
    assert feature["properties"]["project_name"] == "Sundarbans Afforestation"
    assert feature["geometry"]["type"] == "Polygon"

    # 4. Get Site detail
    get_site_res = client.get(f"/api/sites/{site_id}", headers=auth_headers)
    assert get_site_res.status_code == 200
    assert get_site_res.json()["id"] == site_id

    # 5. Delete site
    del_res = client.delete(f"/api/sites/{site_id}", headers=auth_headers)
    assert del_res.status_code == 204
