
from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles

from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.reminder import Reminder
from app.models.user import User


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("ADMIN", "DOCTOR", "RECEPTIONIST")
    )
):

    organization_id = current_user.organization_id

    # ----------------------------------
    # 1. TOTAL ACTIVE PATIENTS
    # ----------------------------------

    total_patients = db.scalar(
        select(func.count())
        .select_from(Patient)
        .where(
            Patient.organization_id == organization_id,
            Patient.is_active == True
        )
    ) or 0


    # ----------------------------------
    # 2. TODAY'S APPOINTMENTS
    # ----------------------------------

    today = datetime.now().date()

    start_of_day = datetime.combine(today, time.min)

    start_of_next_day = start_of_day + timedelta(days=1)

    todays_appointments = db.scalar(
        select(func.count())
        .select_from(Appointment)
        .where(
            Appointment.organization_id == organization_id,
            Appointment.appointment_datetime >= start_of_day,
            Appointment.appointment_datetime < start_of_next_day,
            Appointment.status != "CANCELLED"
        )
    ) or 0


    # ----------------------------------
    # 3. MISSED APPOINTMENTS
    # ----------------------------------

    missed_appointments = db.scalar(
        select(func.count())
        .select_from(Appointment)
        .where(
            Appointment.organization_id == organization_id,
            Appointment.status == "MISSED"
        )
    ) or 0


    # ----------------------------------
    # 4. PENDING REMINDERS
    # ----------------------------------

    pending_reminders = db.scalar(
        select(func.count())
        .select_from(Reminder)
        .where(
            Reminder.organization_id == organization_id,
            Reminder.status == "PENDING"
        )
    ) or 0


    # ----------------------------------
    # 5. RECENT APPOINTMENTS
    # ----------------------------------

    recent_records = db.execute(

        select(
            Appointment.appointment_id,
            Appointment.appointment_datetime,
            Appointment.status,
            Patient.patient_name,
            User.full_name
        )

        .join(
            Patient,
            and_(
                Appointment.patient_id == Patient.patient_id,
                Appointment.organization_id == Patient.organization_id
            )
        )

        .join(
            User,
            and_(
                Appointment.clinician_user_id == User.user_id,
                Appointment.organization_id == User.organization_id
            )
        )

        .where(
            Appointment.organization_id == organization_id
        )

        .order_by(
            Appointment.appointment_datetime.desc()
        )

        .limit(5)

    ).all()


    recent_appointments = []

    for record in recent_records:

        recent_appointments.append({

            "appointment_id": record.appointment_id,

            "patient_name": record.patient_name,

            "appointment_datetime": record.appointment_datetime,

            "doctor_name": record.full_name,

            "status": record.status

        })


    # ----------------------------------
    # RETURN DASHBOARD DATA
    # ----------------------------------

    return {

        "total_patients": total_patients,

        "todays_appointments": todays_appointments,

        "missed_appointments": missed_appointments,

        "pending_reminders": pending_reminders,

        "recent_appointments": recent_appointments

    }
