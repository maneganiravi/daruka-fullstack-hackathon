def test_analytics_and_dashboard_metrics(client, auth_headers):
    # 1. Create a project and a site
    proj_res = client.post(
        "/api/projects",
        json={"name": "Aravalli Forest Project", "target_carbon_sequestration_tons": 20000.0},
        headers=auth_headers,
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    test_polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [77.10, 28.50],
                [77.15, 28.50],
                [77.15, 28.45],
                [77.10, 28.45],
                [77.10, 28.50],
            ]
        ],
    }
    site_res = client.post(
        "/api/sites",
        json={
            "project_id": project_id,
            "name": "Aravalli Ridge Plot 1",
            "geometry": test_polygon,
            "area_hectares": 150.0,
        },
        headers=auth_headers,
    )
    assert site_res.status_code == 201
    site_id = site_res.json()["id"]

    # 2. Add time-series analytics points
    metric_res = client.post(
        f"/api/analytics/sites/{site_id}",
        json={
            "record_date": "2026-01-15",
            "carbon_stored_tons": 1875.0,
            "carbon_rate_per_year": 350.0,
            "biodiversity_score": 74.5,
            "canopy_cover_percentage": 55.0,
            "species_richness_count": 28,
        },
        headers=auth_headers,
    )
    assert metric_res.status_code == 201

    # 3. Retrieve site time series
    ts_res = client.get(f"/api/analytics/sites/{site_id}", headers=auth_headers)
    assert ts_res.status_code == 200
    ts_data = ts_res.json()
    assert ts_data["site_id"] == site_id
    assert len(ts_data["data"]) >= 1

    # 4. Check dashboard metrics endpoint
    dash_res = client.get("/api/analytics/dashboard", headers=auth_headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_projects"] >= 1
    assert dash_data["total_sites"] >= 1
    assert dash_data["total_carbon_stored_tons"] >= 1875.0
