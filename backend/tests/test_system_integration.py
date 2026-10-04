import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.workflow import Workflow, WorkflowStatus
from app.models.business import SalesRecord, SupportTicket, Report
from app.models.document import Document
from app.models.approval import Approval, ApprovalStatus

client = TestClient(app)


def test_health_endpoint():
    """Verify backend health and status."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_auth_login_all_roles():
    """Verify authentication for Admin, Manager, and Employee roles."""
    roles = [
        ("admin@operations.ai", "admin123", "admin"),
        ("manager@operations.ai", "manager123", "manager"),
        ("employee@operations.ai", "employee123", "employee"),
    ]
    for email, pwd, expected_role in roles:
        res = client.post("/api/v1/auth/login", json={"email": email, "password": pwd})
        assert res.status_code == 200, f"Login failed for {email}"
        body = res.json()
        assert "access_token" in body
        assert body["role"] == expected_role


def test_rbac_security_enforcement():
    """Verify that employee cannot access admin or manager-restricted actions."""
    # 1. Login as employee
    emp_res = client.post("/api/v1/auth/login", json={"email": "employee@operations.ai", "password": "employee123"})
    emp_token = emp_res.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # 2. Try to view all users (Admin only)
    users_res = client.get("/api/v1/users", headers=emp_headers)
    assert users_res.status_code == 403, "Employee should NOT be allowed to access /users"

    # 3. Login as admin and access /users
    admin_res = client.post("/api/v1/auth/login", json={"email": "admin@operations.ai", "password": "admin123"})
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_users_res = client.get("/api/v1/users", headers=admin_headers)
    assert admin_users_res.status_code == 200


def test_dashboard_analytics():
    """Verify dashboard KPI statistics generation."""
    login_res = client.post("/api/v1/auth/login", json={"email": "manager@operations.ai", "password": "manager123"})
    token = login_res.json()["access_token"]
    res = client.get("/api/v1/analytics/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert "total_tasks" in data
    assert "total_revenue" in data
    assert "system_health" in data
    assert "agent_activity" in data


def test_document_rag_query():
    """Verify RAG question-answering returns grounded responses."""
    login_res = client.post("/api/v1/auth/login", json={"email": "employee@operations.ai", "password": "employee123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/v1/documents/query",
        headers=headers,
        json={"question": "What is the policy or overview?"}
    )
    assert res.status_code == 200
    body = res.json()
    assert "answer" in body
    assert len(body["answer"]) > 0


def test_report_download_with_token():
    """Verify report downloading with URL token parameter."""
    login_res = client.post("/api/v1/auth/login", json={"email": "manager@operations.ai", "password": "manager123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get reports
    reps_res = client.get("/api/v1/reports", headers=headers)
    assert reps_res.status_code == 200
    reps = reps_res.json()
    if len(reps) > 0:
        rep_id = reps[0]["id"]
        # Download markdown with token
        dl_res = client.get(f"/api/v1/reports/{rep_id}/download?format_type=markdown&token={token}")
        assert dl_res.status_code == 200
        assert len(dl_res.content) > 0
