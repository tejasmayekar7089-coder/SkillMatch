import datetime
from app.database.database import SessionLocal
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.opportunity import Opportunity
from app.models.application import Application
from app.models.enums import ApplicationStatus

db = SessionLocal()

tony = db.query(User).filter(User.email == "iamironman4000@gmail.com").first()
if tony:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == tony.id).first()
    if not profile:
        profile = StudentProfile(
            user_id=tony.id,
            degree="B.Tech in Electrical Engineering",
            major="Electrical Engineering",
            branch="Electrical Engineering",
            academic_year="4th Year / Final",
            gpa=3.95,
            target_role="Embedded Systems Engineer",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Check existing applications
    existing_apps = db.query(Application).filter(Application.student_profile_id == profile.id).all()
    if len(existing_apps) == 0:
        print("Seeding pipeline activities for Tony Stark...")
        opps = db.query(Opportunity).all()
        
        # Pick 6 distinct opportunities across categories
        sample_configs = [
            ("opp-intern-1", ApplicationStatus.DOING, "Hardware Firmware Bench Testing", "Nov 15, 2026", 96, "Running RTOS unit tests on ARM Cortex-M board"),
            ("opp-hack-1", ApplicationStatus.PENDING, "Project Submission Under Review", "Oct 20, 2026", 94, "Submitted Autonomous Robotics prototype"),
            ("opp-schol-1", ApplicationStatus.COMPLETED, "Award Conferred & Completed", "Aug 15, 2026", 98, "Completed all fellowship milestones with Grade A"),
            ("opp-course-1" if any(o.id == "opp-course-1" for o in opps) else opps[0].id, ApplicationStatus.ISSUED, "Proctored Credential Issued", "Sep 01, 2026", 95, "Verified Certificate ID #SM-EE-9941"),
            ("opp-proj-1" if any(o.id == "opp-proj-1" for o in opps) else (opps[1].id if len(opps) > 1 else opps[0].id), ApplicationStatus.APPLIED, "Resume Screen & Technical Round", "Dec 01, 2026", 91, "Application in HR screening queue"),
            ("opp-job-1" if any(o.id == "opp-job-1" for o in opps) else (opps[2].id if len(opps) > 2 else opps[0].id), ApplicationStatus.NOT_COMPLETED, "Archived / Inactive", "Jul 30, 2026", 82, "Withdrawn due to schedule conflict"),
        ]

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        for opp_id, status_val, stage_val, deadline_val, match_val, notes_val in sample_configs:
            # check if opp exists
            opp_obj = db.query(Opportunity).filter(Opportunity.id == opp_id).first()
            if not opp_obj and len(opps) > 0:
                opp_obj = opps[0]
            if opp_obj:
                app_entry = Application(
                    student_profile_id=profile.id,
                    opportunity_id=opp_obj.id,
                    status=status_val,
                    applied_date=datetime.datetime.now(datetime.timezone.utc).strftime("%b %d, %Y"),
                    current_stage=stage_val,
                    next_deadline=deadline_val,
                    match_score=match_val,
                    notes=notes_val,
                    status_history=[
                        {
                            "status": status_val.value if hasattr(status_val, "value") else str(status_val),
                            "stage": stage_val,
                            "timestamp": now_iso,
                            "notes": notes_val,
                        }
                    ],
                )
                db.add(app_entry)
        db.commit()
        print("Successfully seeded pipeline activities for Tony Stark!")

db.close()
