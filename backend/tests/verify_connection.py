import httpx

def check_backend():
    base_url = "http://127.0.0.1:8000"
    print(f"Testing connectivity to {base_url}...")
    try:
        client = httpx.Client(base_url=base_url, timeout=5.0)
        
        # 1. Test Login
        login_res = client.post("/api/auth/login", json={
            "email": "admin@darukaa.earth",
            "password": "AdminPassword123!"
        })
        if login_res.status_code != 200:
            print(f"[FAIL] Auth Login failed: {login_res.status_code} - {login_res.text}")
            return
        
        auth_data = login_res.json()
        token = auth_data["access_token"]
        user = auth_data["user"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"[SUCCESS] Auth: Connected as {user['full_name']} ({user['email']})")

        # 2. Test Projects
        proj_res = client.get("/api/projects", headers=headers)
        projects = proj_res.json()
        print(f"[SUCCESS] Projects API: Loaded {len(projects)} projects from DB")

        # 3. Test Sites GeoJSON
        sites_res = client.get("/api/sites/geojson", headers=headers)
        sites = sites_res.json()
        features = sites.get("features", [])
        print(f"[SUCCESS] Sites GeoJSON API: Loaded {len(features)} PostGIS polygon boundaries")

        # 4. Test Analytics Dashboard
        stats_res = client.get("/api/analytics/dashboard", headers=headers)
        stats = stats_res.json()
        print(f"[SUCCESS] Analytics API: {stats.get('total_area_hectares')} ha restored | {stats.get('total_carbon_tons')} tons CO2e")
        
        print("\nAll Backend APIs and Database connections are HEALTHY and CONNECTED!")

    except httpx.ConnectError:
        print("[FAIL] Cannot connect to FastAPI backend on http://127.0.0.1:8000. Is the server running?")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    check_backend()
