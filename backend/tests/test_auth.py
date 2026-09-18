def test_register_and_login_flow(client):
    # 1. Register a new user
    user_payload = {
        "email": "innovator@darukaa.earth",
        "password": "SecurePassword123!",
        "full_name": "Eco Innovator",
        "role": "user",
    }
    register_res = client.post("/api/auth/register", json=user_payload)
    assert register_res.status_code == 201
    reg_data = register_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "innovator@darukaa.earth"
    assert reg_data["user"]["full_name"] == "Eco Innovator"

    # 2. Duplicate registration should fail
    dup_res = client.post("/api/auth/register", json=user_payload)
    assert dup_res.status_code == 400

    # 3. Login with correct credentials
    login_res = client.post(
        "/api/auth/login",
        json={"email": "innovator@darukaa.earth", "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

    # 4. Login with wrong password should fail
    bad_login = client.post(
        "/api/auth/login",
        json={"email": "innovator@darukaa.earth", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 400

    # 5. Access protected /me route
    token = login_data["access_token"]
    me_res = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "innovator@darukaa.earth"
