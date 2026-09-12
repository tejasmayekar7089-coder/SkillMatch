import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.enums import ApplicationStatus, OpportunityCategory, WorkMode
from app.models.opportunity import Opportunity
from app.models.user import User


def _create_auth_student(client: TestClient, email: str, name: str):
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": name,
            "role": "STUDENT",
            "college": "Test Engineering College",
        },
    )
    assert reg_resp.status_code == 201, reg_resp.text
    token = reg_resp.json()["access_token"]
    user_id = reg_resp.json()["user"]["id"]
    return token, user_id, {"Authorization": f"Bearer {token}"}


def _create_test_opportunity(db_session: Session, opp_id: str, title: str, days_rem: int = 15):
    opp = Opportunity(
        id=opp_id,
        title=title,
        organization="Test Corp AI",
        organization_logo_text="TC",
        organization_subtext="Frontier AI Labs",
        category=OpportunityCategory.INTERNSHIP,
        category_label="Internship",
        domain="Artificial Intelligence",
        location="San Francisco, CA",
        mode=WorkMode.HYBRID,
        compensation="$45/hr",
        deadline="Oct 30, 2026",
        deadline_days_remaining=days_rem,
        posted_ago="1d ago",
        duration="12 weeks",
        cohort_size="10 interns",
        description="Build machine learning systems.",
        key_responsibilities=["Develop models", "Write evaluations"],
        requirements=["Python", "PyTorch"],
        stages=["Application Review", "Technical Interview", "Offer"],
        match_score=92,
        verified=True,
    )
    db_session.add(opp)
    db_session.commit()
    db_session.refresh(opp)
    return opp


def test_saved_opportunities_lifecycle_and_duplicate_prevention(client: TestClient, db_session: Session):
    token_a, user_a, headers_a = _create_auth_student(client, "alice.saved@test.edu", "Alice Saved")
    token_b, user_b, headers_b = _create_auth_student(client, "bob.saved@test.edu", "Bob Saved")
    opp = _create_test_opportunity(db_session, "opp-save-test-1", "AI Research Fellow")

    # 1. Student A saves opportunity
    save_resp = client.post(f"/api/saved/{opp.id}", headers=headers_a)
    assert save_resp.status_code in [200, 201]
    assert save_resp.json()["status"] == "saved"

    # 2. Duplicate prevention: Student A attempts to save the same opportunity again
    dup_save_resp = client.post(f"/api/saved/{opp.id}", headers=headers_a)
    assert dup_save_resp.status_code in [200, 201]
    assert dup_save_resp.json()["status"] == "already_saved"

    # 3. GET /api/saved returns saved opportunity for Student A
    get_saved_a = client.get("/api/saved", headers=headers_a)
    assert get_saved_a.status_code == 200
    saved_list_a = get_saved_a.json()
    assert len(saved_list_a) == 1
    assert saved_list_a[0]["id"] == opp.id
    assert saved_list_a[0]["title"] == "AI Research Fellow"

    # 4. Student isolation: Student B does NOT see Student A's saved opportunity
    get_saved_b = client.get("/api/saved", headers=headers_b)
    assert get_saved_b.status_code == 200
    assert len(get_saved_b.json()) == 0

    # 5. Student A unsaves opportunity
    unsave_resp = client.delete(f"/api/saved/{opp.id}", headers=headers_a)
    assert unsave_resp.status_code == 200
    assert unsave_resp.json()["status"] == "removed"

    # 6. GET /api/saved is now empty for Student A
    get_saved_after = client.get("/api/saved", headers=headers_a)
    assert get_saved_after.status_code == 200
    assert len(get_saved_after.json()) == 0

    # 7. Unsaving again returns 404
    unsave_again = client.delete(f"/api/saved/{opp.id}", headers=headers_a)
    assert unsave_again.status_code == 404


def test_application_tracker_lifecycle_history_and_student_isolation(client: TestClient, db_session: Session):
    token_a, user_a, headers_a = _create_auth_student(client, "alice.tracker@test.edu", "Alice Tracker")
    token_b, user_b, headers_b = _create_auth_student(client, "bob.tracker@test.edu", "Bob Tracker")
    opp = _create_test_opportunity(db_session, "opp-app-test-1", "Fullstack Systems Engineer")

    # 1. Student A applies for opportunity
    apply_payload = {
        "opportunityId": opp.id,
        "status": "APPLIED",
        "appliedDate": "Oct 1, 2026",
        "currentStage": "Application Submitted & Queued",
        "notes": "Highly enthusiastic about distributed systems.",
    }
    create_resp = client.post("/api/applications", json=apply_payload, headers=headers_a)
    assert create_resp.status_code == 201, create_resp.text
    app_data = create_resp.json()
    app_id = app_data["id"]
    assert app_data["opportunityId"] == opp.id
    assert app_data["status"] == "APPLIED"
    assert app_data["opportunityTitle"] == "Fullstack Systems Engineer"
    assert app_data["organization"] == "Test Corp AI"
    assert len(app_data["statusHistory"]) == 1
    assert app_data["statusHistory"][0]["status"] == "APPLIED"
    assert "timestamp" in app_data["statusHistory"][0]

    # 2. Duplicate prevention on application
    dup_apply = client.post("/api/applications", json=apply_payload, headers=headers_a)
    assert dup_apply.status_code == 400
    assert "already been submitted" in dup_apply.json()["detail"]

    # 3. GET /api/applications returns application for Student A
    get_apps_a = client.get("/api/applications", headers=headers_a)
    assert get_apps_a.status_code == 200
    apps_list = get_apps_a.json()
    assert len(apps_list) == 1
    assert apps_list[0]["id"] == app_id

    # 4. Student Isolation: Student B cannot see Student A's application
    get_apps_b = client.get("/api/applications", headers=headers_b)
    assert get_apps_b.status_code == 200
    assert len(get_apps_b.json()) == 0

    # 5. Student Isolation: Student B cannot access Student A's application by ID
    get_single_b = client.get(f"/api/applications/{app_id}", headers=headers_b)
    assert get_single_b.status_code == 403

    # 6. Student Isolation: Student B cannot modify Student A's application
    put_b = client.put(
        f"/api/applications/{app_id}",
        json={"status": "REJECTED"},
        headers=headers_b,
    )
    assert put_b.status_code == 403

    # 7. Student Isolation: Student B cannot delete Student A's application
    del_b = client.delete(f"/api/applications/{app_id}", headers=headers_b)
    assert del_b.status_code == 403

    # 8. Status change transition 1: APPLIED -> SHORTLISTED
    update_1 = client.put(
        f"/api/applications/{app_id}",
        json={
            "status": "SHORTLISTED",
            "currentStage": "Shortlisted for Technical Assessment",
            "notes": "Passed initial resume screening.",
        },
        headers=headers_a,
    )
    assert update_1.status_code == 200
    updated_1_data = update_1.json()
    assert updated_1_data["status"] == "SHORTLISTED"
    assert len(updated_1_data["statusHistory"]) == 2
    assert updated_1_data["statusHistory"][1]["status"] == "SHORTLISTED"
    assert updated_1_data["statusHistory"][1]["previousStatus"] == "APPLIED"

    # 9. Status change transition 2: SHORTLISTED -> INTERVIEW
    update_2 = client.put(
        f"/api/applications/{app_id}",
        json={
            "status": "INTERVIEW",
            "currentStage": "Technical System Design Interview",
            "nextDeadline": "Oct 15, 2026",
            "notes": "Invited to 45-minute live interview.",
        },
        headers=headers_a,
    )
    assert update_2.status_code == 200
    updated_2_data = update_2.json()
    assert updated_2_data["status"] == "INTERVIEW"
    assert len(updated_2_data["statusHistory"]) == 3
    assert updated_2_data["statusHistory"][2]["status"] == "INTERVIEW"

    # 10. GET /api/applications/{id} by Student A succeeds and contains complete status history
    get_single_a = client.get(f"/api/applications/{app_id}", headers=headers_a)
    assert get_single_a.status_code == 200
    single_data = get_single_a.json()
    assert single_data["id"] == app_id
    assert single_data["status"] == "INTERVIEW"
    assert len(single_data["statusHistory"]) == 3

    # 11. Delete application by Student A
    del_a = client.delete(f"/api/applications/{app_id}", headers=headers_a)
    assert del_a.status_code == 200
    assert del_a.json()["status"] == "deleted"

    # 12. Verify deleted
    get_deleted = client.get(f"/api/applications/{app_id}", headers=headers_a)
    assert get_deleted.status_code == 404


def test_notifications_generation_and_mark_read_flow(client: TestClient, db_session: Session):
    token_a, user_a, headers_a = _create_auth_student(client, "alice.notif@test.edu", "Alice Notif")
    token_b, user_b, headers_b = _create_auth_student(client, "bob.notif@test.edu", "Bob Notif")
    opp = _create_test_opportunity(db_session, "opp-notif-test-1", "Cloud Infrastructure Intern")

    # 1. Apply generates application notification
    apply_resp = client.post(
        "/api/applications",
        json={"opportunityId": opp.id, "status": "APPLIED"},
        headers=headers_a,
    )
    assert apply_resp.status_code == 201
    app_id = apply_resp.json()["id"]

    # 2. Status change generates status notification
    update_resp = client.put(
        f"/api/applications/{app_id}",
        json={"status": "SELECTED", "currentStage": "Formal Offer Received"},
        headers=headers_a,
    )
    assert update_resp.status_code == 200

    # 3. GET /api/notifications returns the generated notifications for Student A
    notifs_a = client.get("/api/notifications", headers=headers_a)
    assert notifs_a.status_code == 200
    notif_list_a = notifs_a.json()
    assert len(notif_list_a) >= 2

    # Check notification types and titles
    titles = [n["title"] for n in notif_list_a]
    assert any("Application Submitted" in t for t in titles)
    assert any("Status Update" in t for t in titles)

    # 4. Student Isolation: Student B has 0 notifications
    notifs_b = client.get("/api/notifications", headers=headers_b)
    assert notifs_b.status_code == 200
    assert len(notifs_b.json()) == 0

    # 5. Student B cannot mark Student A's notification as read
    first_notif_id = notif_list_a[0]["id"]
    mark_b = client.put(f"/api/notifications/{first_notif_id}/read", headers=headers_b)
    assert mark_b.status_code == 404

    # 6. Student A marks single notification as read
    mark_a = client.put(f"/api/notifications/{first_notif_id}/read", headers=headers_a)
    assert mark_a.status_code == 200
    assert mark_a.json()["status"] == "ok"

    # Verify that single notification is read
    notifs_after_mark = client.get("/api/notifications", headers=headers_a).json()
    marked_item = next(n for n in notifs_after_mark if n["id"] == first_notif_id)
    assert marked_item["read"] is True

    # 7. Student A marks all notifications as read
    mark_all = client.put("/api/notifications/read-all", headers=headers_a)
    assert mark_all.status_code == 200
    assert mark_all.json()["status"] == "ok"

    # Verify all notifications are read
    notifs_all_read = client.get("/api/notifications", headers=headers_a).json()
    assert all(n["read"] is True for n in notifs_all_read)


def test_approaching_deadline_notification_and_duplicate_prevention(client: TestClient, db_session: Session):
    token, user_id, headers = _create_auth_student(client, "alice.deadline@test.edu", "Alice Deadline")

    # Opportunity with approaching deadline (3 days remaining <= 5)
    urgent_opp = _create_test_opportunity(
        db_session, "opp-deadline-urgent-1", "Quantum Computing Research Fellowship", days_rem=3
    )

    # Save the opportunity
    save_resp = client.post(f"/api/saved/{urgent_opp.id}", headers=headers)
    assert save_resp.status_code in [200, 201]

    # Fetch notifications: approaching deadline detection runs automatically
    notifs_1 = client.get("/api/notifications", headers=headers).json()
    deadline_notifs_1 = [n for n in notifs_1 if n["type"] == "deadline"]
    assert len(deadline_notifs_1) == 1
    assert "Approaching Deadline" in deadline_notifs_1[0]["title"]
    assert "closes in 3 days" in deadline_notifs_1[0]["description"]

    # Call GET /api/notifications again: verify duplicate prevention
    notifs_2 = client.get("/api/notifications", headers=headers).json()
    deadline_notifs_2 = [n for n in notifs_2 if n["type"] == "deadline"]
    assert len(deadline_notifs_2) == 1, "Duplicate deadline notification must not be created!"
