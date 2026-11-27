
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Appointment, Patient, User
from app.schemas.appointments import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/appointments",
    tags=["Appointments"]
)


# ==========================================
# VALIDATE PATIENT
# ==========================================

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active patient not found in this organization"
        )

    return patient


# ==========================================
# VALIDATE DOCTOR
# ==========================================

def validate_doctor(
    db: Session,
    clinician_user_id: str,
    organization_id: str
):
    doctor = db.scalar(
        select(User).where(
            User.user_id == clinician_user_id,
            User.organization_id == organization_id,
            User.is_active == True,
            User.role == "DOCTOR"
        )
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active doctor not found in this organization"
        )

    return doctor


# ==========================================
# CREATE APPOINTMENT
# ==========================================

@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    organization_id = current_user.organization_id

    validate_patient(
        db,
        data.patient_id,
        organization_id
    )

    validate_doctor(
        db,
        data.clinician_user_id,
        organization_id
    )

    appointment = Appointment(
        organization_id=organization_id,
        patient_id=data.patient_id,
        clinician_user_id=data.clinician_user_id,
        appointment_datetime=data.appointment_datetime,
        appointment_type=data.appointment_type,
        reason=data.reason,
        notes=data.notes,
        created_by=current_user.user_id
    )

    db.add(appointment)
    db.flush()

    create_audit_log(
        db=db,
        organization_id=organization_id,
        actor_user_id=current_user.user_id,
        action="APPOINTMENT_CREATED",
        entity_type="APPOINTMENT",
        entity_id=appointment.appointment_id,
        details={
            "patient_id": data.patient_id,
            "clinician_user_id": data.clinician_user_id,
            "appointment_type": data.appointment_type
        }
    )

    db.commit()
    db.refresh(appointment)

    return appointment


# ==========================================
# GET ALL APPOINTMENTS
# ==========================================

@router.get(
    "/",
    response_model=list[AppointmentResponse]
)
def get_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appointments = db.scalars(
        select(Appointment).where(
            Appointment.organization_id
            == current_user.organization_id
        ).order_by(
            Appointment.appointment_datetime
        )
    ).all()

    return appointments


# ==========================================
# GET APPOINTMENT BY ID
# ==========================================

@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def get_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appointment = db.scalar(
        select(Appointment).where(
            Appointment.appointment_id == str(appointment_id),
            Appointment.organization_id
            == current_user.organization_id
        )
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    return appointment


# ==========================================
# UPDATE APPOINTMENT
# ==========================================

@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def update_appointment(
    appointment_id: UUID,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appointment = db.scalar(
        select(Appointment).where(
            Appointment.appointment_id == str(appointment_id),
            Appointment.organization_id
            == current_user.organization_id
        )
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided"
        )

    if (
        "patient_id" in update_data
        and update_data["patient_id"] is not None
    ):
        validate_patient(
            db,
            update_data["patient_id"],
            current_user.organization_id
        )

    if (
        "clinician_user_id" in update_data
        and update_data["clinician_user_id"] is not None
    ):
        validate_doctor(
            db,
            update_data["clinician_user_id"],
            current_user.organization_id
        )

    updated_fields = []

    for field, value in update_data.items():
        if value is not None:
            setattr(appointment, field, value)
            updated_fields.append(field)

    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )

    create_audit_log(
        db=db,
        organization_id=current_user.organization_id,
        actor_user_id=current_user.user_id,
        action="APPOINTMENT_UPDATED",
        entity_type="APPOINTMENT",
        entity_id=appointment.appointment_id,
        details={
            "updated_fields": updated_fields
        }
    )

    db.commit()
    db.refresh(appointment)

    return appointment


# ==========================================
# CANCEL APPOINTMENT
# ==========================================

@router.delete(
    "/{appointment_id}"
)
def cancel_appointment(
    appointment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    appointment = db.scalar(
        select(Appointment).where(
            Appointment.appointment_id == str(appointment_id),
            Appointment.organization_id
            == current_user.organization_id
        )
    )

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    if appointment.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already cancelled"
        )

    previous_status = appointment.status

    appointment.status = "CANCELLED"

    create_audit_log(
        db=db,
        organization_id=current_user.organization_id,
        actor_user_id=current_user.user_id,
        action="APPOINTMENT_CANCELLED",
        entity_type="APPOINTMENT",
        entity_id=appointment.appointment_id,
        details={
            "patient_id": appointment.patient_id,
            "previous_status": previous_status,
            "new_status": "CANCELLED"
        }
    )

    db.commit()
    db.refresh(appointment)

    return {
        "message": "Appointment cancelled successfully",
        "appointment_id": appointment.appointment_id,
        "status": appointment.status
    }
