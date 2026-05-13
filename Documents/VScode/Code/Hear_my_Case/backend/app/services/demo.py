"""Demo data bootstrap helpers."""
from __future__ import annotations

import io
import uuid

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseStep, CaseStatus, CaseType
from app.models.evidence import Evidence
from app.models.group import Group
from app.models.lawyer import Lawyer
from app.models.ngo import NGO
from app.models.notification import Notification
from app.models.user import User, UserRole
from app.services.ai import generate_case_analysis
from app.services.storage import store_upload

DEMO_WORKER_PHONE = "+919900000001"
DEMO_WORKER_PASSWORD = "Demo@1234"
DEMO_ADMIN_PHONE = "+919900000099"
DEMO_ADMIN_PASSWORD = "Admin@1234"
DEMO_LAWYER_PHONE = "+919900000002"
DEMO_LAWYER_PASSWORD = "Lawyer@1234"


def _hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


async def seed_demo_data(db: AsyncSession) -> dict[str, object]:
    """Seed a complete demo dataset if it is not already present."""
    existing = await db.execute(select(User).where(User.phone_number == DEMO_WORKER_PHONE))
    if existing.scalars().first():
        return {"seeded": False, "message": "Demo data already exists"}

    worker = User(
        id=uuid.uuid4(),
        phone_number=DEMO_WORKER_PHONE,
        full_name="Demo Worker",
        email="worker.demo@hear-my-case.local",
        password_hash=_hash_password(DEMO_WORKER_PASSWORD),
        role=UserRole.WORKER,
        is_active=True,
        is_verified=True,
        state="Maharashtra",
        bio="Factory worker with an unpaid wages claim",
    )

    admin = User(
        id=uuid.uuid4(),
        phone_number=DEMO_ADMIN_PHONE,
        full_name="Demo Admin",
        email="admin.demo@hear-my-case.local",
        password_hash=_hash_password(DEMO_ADMIN_PASSWORD),
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        is_verified=True,
        state="Karnataka",
        bio="Platform administrator",
    )

    lawyer_user = User(
        id=uuid.uuid4(),
        phone_number=DEMO_LAWYER_PHONE,
        full_name="Demo Lawyer User",
        email="lawyer.demo@hear-my-case.local",
        password_hash=_hash_password(DEMO_LAWYER_PASSWORD),
        role=UserRole.LAWYER,
        is_active=True,
        is_verified=True,
        state="Maharashtra",
        bio="Labor law specialist",
    )

    db.add_all([worker, admin, lawyer_user])
    await db.flush()

    ngo = NGO(
        id=uuid.uuid4(),
        name="Workers Justice Collective",
        email="contact@workersjustice.local",
        phone_number="+910000000010",
        description="Supports wage recovery and workplace rights cases.",
        website="https://workersjustice.local",
        states_served=["Maharashtra", "Karnataka"],
        case_types_handled=["unpaid_wages", "harassment", "wrongful_termination"],
        is_active=True,
        contact_person_name="Priya Nair",
        contact_person_phone="+910000000011",
        average_rating="4.9",
        total_cases_handled=128,
    )

    lawyer = Lawyer(
        id=uuid.uuid4(),
        user_id=lawyer_user.id,
        full_name="Adv. Meera Iyer",
        phone_number=DEMO_LAWYER_PHONE,
        email="meera.iyer@hear-my-case.local",
        bio="Handles labor disputes and wage claims.",
        years_of_experience=12,
        specializations=["labor_law", "wage_disputes"],
        bar_council_id="BAR-2026-DEMO",
        is_available=True,
        available_for_group_cases=True,
        states_served=["Maharashtra", "Karnataka"],
        average_rating="4.8",
        total_cases=241,
        active_cases=8,
        office_address="Mumbai, Maharashtra",
        languages=["en", "hi", "mr"],
    )

    group = Group(
        id=uuid.uuid4(),
        state="Maharashtra",
        case_type="unpaid_wages",
        notice_status="sent",
        assigned_lawyer_id=lawyer.id,
        member_count=14,
        notice_url="/uploads/demo/collective-notice.txt",
    )

    case = Case(
        id=uuid.uuid4(),
        user_id=worker.id,
        case_type=CaseType.UNPAID_WAGES,
        status=CaseStatus.REPORT_GENERATED,
        employer_name="ABC Manufacturing Pvt Ltd",
        amount_owed=76000.0,
        period_start="2025-01-01",
        period_end="2025-04-30",
        contract_type="written",
        group_id=group.id,
        lawyer_id=lawyer.id,
    )

    analysis = await generate_case_analysis(
        {
            "case_type": case.case_type.value,
            "employer_name": case.employer_name,
            "amount_owed": case.amount_owed,
            "period_start": case.period_start,
            "period_end": case.period_end,
            "contract_type": case.contract_type,
            "evidence_count": 1,
        }
    )
    case.case_summary = analysis.get("case_summary")
    case.applicable_laws = analysis.get("applicable_laws")
    case.what_should_happen = analysis.get("what_should_happen")
    case.next_steps = analysis.get("next_steps")

    db.add_all([ngo, lawyer, group, case])
    await db.flush()

    case_steps = [
        CaseStep(
            case_id=case.id,
            step_number="1",
            title="Review facts",
            description="Confirm wages, dates, and employment relationship.",
            status="completed",
        ),
        CaseStep(
            case_id=case.id,
            step_number="2",
            title="Collect evidence",
            description="Upload wage slips, messages, and appointment documents.",
            status="completed",
        ),
        CaseStep(
            case_id=case.id,
            step_number="3",
            title="Send notice",
            description="Prepare and send a formal demand to the employer.",
            status="in_progress",
        ),
    ]

    demo_notice = b"Collective notice issued for unpaid wages demo case."
    file_url = store_upload(io.BytesIO(demo_notice), "demo/collective-notice.txt", content_type="text/plain")
    evidence = Evidence(
        id=uuid.uuid4(),
        case_id=case.id,
        file_name="collective-notice.txt",
        file_url=file_url,
        file_size=str(len(demo_notice)),
        mime_type="text/plain",
        category="contract",
        confidence_score="0.88",
        auto_tags=["notice", "collective", "wages"],
        extracted_text=demo_notice.decode("utf-8"),
        ai_summary="Collective notice for a group unpaid wages case.",
        user_description="Demo collective notice prepared by the legal team.",
    )

    notifications = [
        Notification(
            user_id=worker.id,
            title="Case analysis ready",
            message="Your unpaid wages case has been reviewed and the next steps are available.",
            notification_type="success",
            is_read=False,
            is_sent=True,
            related_case_id=case.id,
        ),
        Notification(
            user_id=worker.id,
            title="Evidence received",
            message="The uploaded evidence has been indexed and tagged.",
            notification_type="info",
            is_read=False,
            is_sent=True,
            related_case_id=case.id,
        ),
    ]

    db.add_all(case_steps + [evidence] + notifications)
    await db.commit()

    return {
        "seeded": True,
        "message": "Demo data created successfully",
        "credentials": {
            "worker_phone": DEMO_WORKER_PHONE,
            "worker_password": DEMO_WORKER_PASSWORD,
            "admin_phone": DEMO_ADMIN_PHONE,
            "admin_password": DEMO_ADMIN_PASSWORD,
            "lawyer_phone": DEMO_LAWYER_PHONE,
            "lawyer_password": DEMO_LAWYER_PASSWORD,
        },
    }
