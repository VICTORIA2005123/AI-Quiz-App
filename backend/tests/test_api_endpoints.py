import time
import io
from fastapi.testclient import TestClient


def test_health_and_version_endpoints(client: TestClient):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"

    v_resp = client.get("/api/v1/version")
    assert v_resp.status_code == 200
    v_data = v_resp.json()
    assert v_data["api_version"] == "v1"


def test_user_registration_and_auth_flow(client: TestClient):
    email = "testuser@example.com"
    password = "SecurePassword123!"

    # 1. Register
    reg_resp = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert reg_resp.status_code == 200
    user_data = reg_resp.json()
    assert user_data["email"] == email

    # 2. Login
    login_resp = client.post("/api/v1/auth/token", json={"email": email, "password": password})
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Profile /me
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == email

    # 4. Quota check
    quota_resp = client.get("/api/v1/auth/quota", headers=headers)
    assert quota_resp.status_code == 200
    assert quota_resp.json()["daily_limit"] >= 1


def test_submit_document_and_poll_job_flow(client: TestClient):
    # Register & get token
    email = "jobtester@example.com"
    password = "Password12345!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    tokens = client.post("/api/v1/auth/token", json={"email": email, "password": password}).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Prepare sample document
    doc_content = (
        "# Cellular Biology Lecture\n"
        "Mitochondria are known as the powerhouse of the cell. "
        "They produce adenosine triphosphate (ATP) via oxidative phosphorylation. "
        "The inner membrane is folded into cristae to increase surface area."
    )
    file_bytes = io.BytesIO(doc_content.encode("utf-8"))

    # Submit job
    files = {"file": ("biology_lecture.md", file_bytes, "text/markdown")}
    data = {"question_count": 2, "difficulty": "medium", "bloom_level": "understand"}
    submit_resp = client.post("/api/v1/jobs", headers=headers, files=files, data=data)
    assert submit_resp.status_code == 202
    job_info = submit_resp.json()
    job_id = job_info["job_id"]
    assert job_info["status"] in ["QUEUED", "VALIDATING_FILE", "PARSING", "GENERATING", "COMPLETED"]

    # Poll status (with brief wait for worker thread)
    time.sleep(1.0)
    poll_resp = client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert poll_resp.status_code == 200
    status_data = poll_resp.json()
    assert status_data["job_id"] == job_id
    assert status_data["status"] in ["QUEUED", "PARSING", "NORMALIZING", "CHUNKING", "PII_PROCESSING", "GENERATING", "VERIFYING_EVIDENCE", "COMPLETED"]


def test_job_cancellation_flow(client: TestClient):
    email = "canceltester@example.com"
    password = "Password12345!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    tokens = client.post("/api/v1/auth/token", json={"email": email, "password": password}).json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    doc_content = "Brief notes for testing cancellation."
    file_bytes = io.BytesIO(doc_content.encode("utf-8"))
    files = {"file": ("notes.txt", file_bytes, "text/plain")}
    submit_resp = client.post("/api/v1/jobs", headers=headers, files=files)
    job_id = submit_resp.json()["job_id"]

    # Cancel job
    cancel_resp = client.post(f"/api/v1/jobs/{job_id}/cancel", headers=headers)
    assert cancel_resp.status_code in [200, 400]  # 200 if cancelled in time, 400 if already finished immediately
