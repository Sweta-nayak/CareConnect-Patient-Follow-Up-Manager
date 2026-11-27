
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models.reminder import Reminder
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.care_instruction import CareInstruction
from app.schemas.reminder import ReminderCreate, ReminderResponse


router = APIRouter(
    prefix="/api/reminders",
    tags=["Reminders"]
)


# --------------------------------------------------
# VALIDATE PATIENT
# --------------------------------------------------

def validate_patient(
    db: Session,
    patient_id: str,
    organization_id: str
):
    patient = db.scalar(
        select(Patient).where(
            Patient.patient_id == patient_id,
            Patient.organization_id == organization_id,
            Patient.is_active == True
        )
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found or inactive"
        )

    return patient


# --------------------------------------------------
# VALIDATE APPOINTMENT
# --------------------------------------------------

def validate_appointment(
    db: Session,
    appointment_id: str,
    patient_id: str,
    organization_id: str
):
    appointment = db.scalar(
        select(Appointment).where(
            Appointment.appointment_id == appointment_id,
            Appointment.organization_id == organization_id,
            Appointment.patient_id == patient_id
        )
    )

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found for this patient"
        )

    if appointment.status in ["CANCELLED", "MISSED"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot create a reminder for a cancelled or missed appointment"
        )

    return appointment


# --------------------------------------------------
# VALIDATE CARE INSTRUCTION
# --------------------------------------------------

def validate_instruction(
    db: Session,
    instruction_id: str,
    patient_id: str,
    organization_id: str,
    reminder_type: str
):
    instruction = db.scalar(
        select(CareInstruction).where(
            CareInstruction.instruction_id == instruction_id,
            CareInstruction.organization_id == organization_id,
            CareInstruction.patient_id == patient_id
        )
    )

    if not instruction:
        raise HTTPException(
            status_code=404,
            detail="Care instruction not found for this patient"
        )

    if instruction.approval_status != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail="Only approved care instructions can have reminders"
        )

    if instruction.instruction_type != reminder_type:
        raise HTTPException(
            status_code=400,
            detail="Reminder type does not match the care instruction type"
        )

    return instruction


# --------------------------------------------------
# CREATE REMINDER
# --------------------------------------------------

@router.post(
    "/",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED
)
def create_reminder(
    reminder_data: ReminderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("ADMIN", "DOCTOR", "RECEPTIONIST")
    )
):

    organization_id = current_user.organization_id

    # Validate patient
    validate_patient(
        db,
        reminder_data.patient_id,
        organization_id
    )

    # Validate appointment or care instruction
    if reminder_data.reminder_type == "APPOINTMENT":

        validate_appointment(
            db,
            reminder_data.appointment_id,
            reminder_data.patient_id,
            organization_id
        )

    else:

        validate_instruction(
            db,
            reminder_data.instruction_id,
            reminder_data.patient_id,
            organization_id,
            reminder_data.reminder_type
        )

    # Check for an existing idempotency key
    existing_reminder = db.scalar(
        select(Reminder).where(
            Reminder.organization_id == organization_id,
            Reminder.idempotency_key == reminder_data.idempotency_key
        )
    )

    if existing_reminder:
        raise HTTPException(
            status_code=409,
            detail="A reminder with this idempotency key already exists"
        )

    # Create reminder
    new_reminder = Reminder(
        organization_id=organization_id,
        patient_id=reminder_data.patient_id,
        instruction_id=reminder_data.instruction_id,
        appointment_id=reminder_data.appointment_id,
        channel=reminder_data.channel,
        reminder_type=reminder_data.reminder_type,
        scheduled_at=reminder_data.scheduled_at,
        message_text=reminder_data.message_text,
        idempotency_key=reminder_data.idempotency_key,
        status="PENDING"
    )

    db.add(new_reminder)

    try:
        db.commit()
        db.refresh(new_reminder)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Duplicate reminder or invalid linked record"
        )

    return new_reminder


# --------------------------------------------------
# GET ALL REMINDERS
# --------------------------------------------------

@router.get(
    "/",
    response_model=list[ReminderResponse]
)
def get_reminders(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("ADMIN", "DOCTOR", "RECEPTIONIST")
    )
):

    reminders = db.scalars(
        select(Reminder)
        .where(
            Reminder.organization_id == current_user.organization_id
        )
        .order_by(Reminder.scheduled_at.desc())
    ).all()

    return reminders


# --------------------------------------------------
# GET REMINDER BY ID
# --------------------------------------------------

@router.get(
    "/{reminder_id}",
    response_model=ReminderResponse
)
def get_reminder(
    reminder_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("ADMIN", "DOCTOR", "RECEPTIONIST")
    )
):

    reminder = db.scalar(
        select(Reminder).where(
            Reminder.reminder_id == reminder_id,
            Reminder.organization_id == current_user.organization_id
        )
    )

    if not reminder:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found"
        )

    return reminder


# --------------------------------------------------
# SIMULATE REMINDER DELIVERY
# --------------------------------------------------

@router.patch(
    "/{reminder_id}/simulate",
    response_model=ReminderResponse
)
def simulate_reminder(
    reminder_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("ADMIN", "RECEPTIONIST")
    )
):

    reminder = db.scalar(
        select(Reminder).where(
            Reminder.reminder_id == reminder_id,
            Reminder.organization_id == current_user.organization_id
        )
    )

    if not reminder:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found"
        )

    if reminder.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Only pending reminders can be simulated"
        )

    if reminder.scheduled_at > datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Reminder is not due yet"
        )

    # Simulate delivery; no real SMS or WhatsApp is sent
    reminder.status = "SIMULATED"
    reminder.attempted_at = datetime.now()

    db.commit()
    db.refresh(reminder)

    return reminder


# --------------------------------------------------
# CANCEL REMINDER
# --------------------------------------------------

@router.patch(
    "/{reminder_id}/cancel",
    response_model=ReminderResponse
)
def cancel_reminder(
    reminder_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("ADMIN", "DOCTOR", "RECEPTIONIST")
    )
):

    reminder = db.scalar(
        select(Reminder).where(
            Reminder.reminder_id == reminder_id,
            Reminder.organization_id == current_user.organization_id
        )
    )

    if not reminder:
        raise HTTPException(
            status_code=404,
            detail="Reminder not found"
        )

    if reminder.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Only pending reminders can be cancelled"
        )

    reminder.status = "CANCELLED"

    db.commit()
    db.refresh(reminder)

    return reminder
