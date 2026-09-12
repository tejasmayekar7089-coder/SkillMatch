import pytest
from fastapi.testclient import TestClient


def test_auth_and_student_profile_lifecycle(client: TestClient):
    # 1. Register a new student
    register_payload = {
        "email": "sarah.connor@cyberdyne.edu",
        "password": "SecurePassword123!",
        "full_name": "Sarah Connor",
        "role": "STUDENT",
        "college": "MIT University",
    }
    reg_resp = client.post("/api/auth/register", json=register_payload)
    assert reg_resp.status_code == 201, reg_resp.text
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "sarah.connor@cyberdyne.edu"
    assert reg_data["user"]["role"] == "STUDENT"
    token = reg_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Duplicate registration attempt must fail with 400
    dup_resp = client.post("/api/auth/register", json=register_payload)
    assert dup_resp.status_code == 400
    assert "already exists" in dup_resp.json()["detail"]

    # 3. Login with invalid password must fail with 401
    bad_login = client.post(
        "/api/auth/login",
        json={"email": "sarah.connor@cyberdyne.edu", "password": "WrongPassword"},
    )
    assert bad_login.status_code == 401
    assert "Invalid email or password" in bad_login.json()["detail"]

    # 4. Login with correct credentials
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "sarah.connor@cyberdyne.edu", "password": "SecurePassword123!"},
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # 5. /api/auth/me without token -> 401
    unauth_resp = client.get("/api/auth/me")
    assert unauth_resp.status_code == 401

    # 6. /api/auth/me with valid token -> 200
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "sarah.connor@cyberdyne.edu"
    assert me_resp.json()["full_name"] == "Sarah Connor"

    # 7. Get initial profile
    prof_resp = client.get("/api/profile", headers=headers)
    assert prof_resp.status_code == 200
    prof_data = prof_resp.json()
    assert prof_data["email"] == "sarah.connor@cyberdyne.edu"
    assert prof_data["college"] == "MIT University"

    # 8. Update profile with full academic and preference details
    update_payload = {
        "full_name": "Sarah J. Connor",
        "college": "Massachusetts Institute of Technology",
        "degree": "B.S. in Computer Science",
        "branch": "Artificial Intelligence",
        "academic_year": "Senior Year",
        "graduation_year": "2026",
        "gpa": 3.92,
        "preferred_domains": ["AI / Machine Learning", "Robotics", "Autonomous Systems"],
        "preferred_locations": ["San Francisco, CA", "Boston, MA", "Remote"],
        "preferred_work_mode": "Hybrid",
        "experience": "2 internships in AI research labs",
        "bio": "Passionate about robust AI architectures and trustworthy systems.",
        "target_role": "Machine Learning Engineer",
    }
    put_resp = client.put("/api/profile", json=update_payload, headers=headers)
    assert put_resp.status_code == 200
    updated_prof = put_resp.json()
    assert updated_prof["full_name"] == "Sarah J. Connor"
    assert updated_prof["college"] == "Massachusetts Institute of Technology"
    assert updated_prof["gpa"] == 3.92
    assert "Robotics" in updated_prof["preferred_domains"]
    assert updated_prof["bio"] == "Passionate about robust AI architectures and trustworthy systems."

    # 9. Skills: Add Skill 1 (Python, Advanced)
    skill1_resp = client.post(
        "/api/profile/skills",
        json={"name": "Python", "proficiency": "Advanced", "category": "Languages"},
        headers=headers,
    )
    assert skill1_resp.status_code == 201
    s1 = skill1_resp.json()
    assert s1["name"] == "Python"
    assert s1["normalized_name"] == "python"
    assert s1["proficiency"] == "Advanced"

    # 10. Skills: Prevent duplicate (case-insensitive "python") -> updates existing proficiency
    skill1_dup = client.post(
        "/api/profile/skills",
        json={"name": "python", "proficiency": "Expert"},
        headers=headers,
    )
    assert skill1_dup.status_code in [200, 201]
    assert skill1_dup.json()["id"] == s1["id"]
    assert skill1_dup.json()["proficiency"] == "Expert"

    # 11. Skills: Add Skill 2 (PyTorch)
    skill2_resp = client.post(
        "/api/profile/skills",
        json={"name": "PyTorch", "proficiency": "Intermediate", "category": "Frameworks"},
        headers=headers,
    )
    assert skill2_resp.status_code == 201
    s2_id = skill2_resp.json()["id"]

    # 12. Skills: Update Skill 2
    put_skill_resp = client.put(
        f"/api/profile/skills/{s2_id}",
        json={"proficiency": "Advanced", "progress_percent": 90},
        headers=headers,
    )
    assert put_skill_resp.status_code == 200
    assert put_skill_resp.json()["proficiency"] == "Advanced"
    assert put_skill_resp.json()["progress_percent"] == 90

    # 13. Skills: List skills
    list_skills = client.get("/api/profile/skills", headers=headers)
    assert list_skills.status_code == 200
    assert len(list_skills.json()) == 2

    # 14. Interests: Add interest
    int_resp = client.post(
        "/api/profile/interests",
        json={"name": "Reinforcement Learning", "category": "AI"},
        headers=headers,
    )
    assert int_resp.status_code == 201
    int_id = int_resp.json()["id"]

    # Interests: Duplicate check
    int_dup = client.post(
        "/api/profile/interests",
        json={"name": "Reinforcement Learning"},
        headers=headers,
    )
    assert int_dup.status_code in [200, 201]

    # Interests: List
    list_int = client.get("/api/profile/interests", headers=headers)
    assert list_int.status_code == 200
    assert len(list_int.json()) == 1

    # 15. Projects: Create Project
    proj_resp = client.post(
        "/api/profile/projects",
        json={
            "title": "Autonomous Quadrotor Navigation",
            "description": "Obstacle avoidance via deep reinforcement learning with PyTorch and ROS.",
            "technologies": ["Python", "PyTorch", "ROS2", "Gazebo"],
            "skills": ["Python", "Reinforcement Learning"],
            "project_url": "https://sarahconnor.dev/quadrotor",
            "github_url": "https://github.com/sarahconnor/quadrotor-nav",
            "start_date": "2025-09-01",
            "end_date": "2026-01-15",
        },
        headers=headers,
    )
    assert proj_resp.status_code == 201
    proj = proj_resp.json()
    assert proj["title"] == "Autonomous Quadrotor Navigation"
    proj_id = proj["id"]

    # Projects: Get by ID
    get_proj = client.get(f"/api/profile/projects/{proj_id}", headers=headers)
    assert get_proj.status_code == 200
    assert get_proj.json()["title"] == "Autonomous Quadrotor Navigation"

    # Projects: Update
    put_proj = client.put(
        f"/api/profile/projects/{proj_id}",
        json={"description": "Updated high-precision flight control pipeline."},
        headers=headers,
    )
    assert put_proj.status_code == 200
    assert put_proj.json()["description"] == "Updated high-precision flight control pipeline."

    # 16. Certifications: Create Certification
    cert_resp = client.post(
        "/api/profile/certifications",
        json={
            "name": "AWS Certified Machine Learning - Specialty",
            "issuing_organization": "Amazon Web Services",
            "issue_date": "2025-11-10",
            "credential_id": "AWS-MLS-987654",
            "credential_url": "https://aws.amazon.com/verify/987654",
        },
        headers=headers,
    )
    assert cert_resp.status_code == 201
    cert = cert_resp.json()
    assert cert["name"] == "AWS Certified Machine Learning - Specialty"
    cert_id = cert["id"]

    # Certifications: Get by ID
    get_cert = client.get(f"/api/profile/certifications/{cert_id}", headers=headers)
    assert get_cert.status_code == 200
    assert get_cert.json()["credential_id"] == "AWS-MLS-987654"

    # Certifications: Update
    put_cert = client.put(
        f"/api/profile/certifications/{cert_id}",
        json={"issue_date": "2025-12-01"},
        headers=headers,
    )
    assert put_cert.status_code == 200
    assert put_cert.json()["issue_date"] == "2025-12-01"

    # 17. Retrieve Complete Profile and verify nested objects
    full_profile = client.get("/api/profile", headers=headers)
    assert full_profile.status_code == 200
    fp = full_profile.json()
    assert fp["full_name"] == "Sarah J. Connor"
    assert len(fp["skills"]) == 2
    assert len(fp["interests"]) == 1
    assert len(fp["projects"]) == 1
    assert len(fp["certifications"]) == 1

    # 18. Delete operations
    del_skill = client.delete(f"/api/profile/skills/{s2_id}", headers=headers)
    assert del_skill.status_code == 200

    del_int = client.delete(f"/api/profile/interests/{int_id}", headers=headers)
    assert del_int.status_code == 200

    del_proj = client.delete(f"/api/profile/projects/{proj_id}", headers=headers)
    assert del_proj.status_code == 200

    del_cert = client.delete(f"/api/profile/certifications/{cert_id}", headers=headers)
    assert del_cert.status_code == 200

    # Verify counts after deletes
    final_profile = client.get("/api/profile", headers=headers).json()
    assert len(final_profile["skills"]) == 1
    assert len(final_profile["interests"]) == 0
    assert len(final_profile["projects"]) == 0
    assert len(final_profile["certifications"]) == 0
