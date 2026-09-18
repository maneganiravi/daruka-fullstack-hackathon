def test_create_and_get_project(client, auth_headers):
    # 1. Create a project
    project_data = {
        "name": "Western Ghats Corridor Restoration",
        "description": "Connecting fragmented rainforest patches in Kerala.",
        "client_name": "Wildlife Trust of India",
        "status": "active",
        "target_carbon_sequestration_tons": 50000.0,
    }
    create_res = client.post("/api/projects", json=project_data, headers=auth_headers)
    assert create_res.status_code == 201
    created_project = create_res.json()
    project_id = created_project["id"]
    assert created_project["name"] == "Western Ghats Corridor Restoration"
    assert created_project["status"] == "active"
    assert created_project["sites_count"] == 0

    # 2. List projects
    list_res = client.get("/api/projects", headers=auth_headers)
    assert list_res.status_code == 200
    projects = list_res.json()
    assert len(projects) >= 1
    assert any(p["id"] == project_id for p in projects)

    # 3. Get project details
    detail_res = client.get(f"/api/projects/{project_id}", headers=auth_headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == project_id
    assert "sites" in detail
    assert isinstance(detail["sites"], list)

    # 4. Update project
    update_res = client.put(
        f"/api/projects/{project_id}",
        json={"name": "Western Ghats Corridor Phase 2", "status": "active"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Western Ghats Corridor Phase 2"

    # 5. Delete project
    del_res = client.delete(f"/api/projects/{project_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # Verify not found
    get_after_del = client.get(f"/api/projects/{project_id}", headers=auth_headers)
    assert get_after_del.status_code == 404
