
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user

from app.models.patient import Patient
from app.models.user import User

from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse
)

from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"]
)


# =====================================
# 1. CREATE PATIENT
# =====================================

@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_patient = Patient(
        **patient_data.model_dump(),
        organization_id=current_user.organization_id,
        created_by=current_user.user_id
    )

    db.add(new_patient)

    create_audit_log(
        db=db,
        organization_id=current_user.organization_id,
        actor_user_id=current_user.user_id,
        action="PATIENT_CREATED",
        entity_type="PATIENT",
        entity_id=new_patient.patient_id,
        details={
            "patient_name": new_patient.patient_name
        }
    )

    db.commit()
    db.refresh(new_patient)

    return new_patient


# =====================================
# 2. GET ALL PATIENTS
# =====================================

@router.get(
    "/",
    response_model=list[PatientResponse]
)
def get_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = select(Patient).where(
        Patient.organization_id == current_user.organization_id,
        Patient.is_active == True
    )

    patients = db.scalars(query).all()

    return patients


# =====================================
# 3. GET PATIENT BY ID
# =====================================

@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    patient = db.scalar(
        select(Patient).where(
            Patient.patient_id == patient_id,
            Patient.organization_id == current_user.organization_id,
            Patient.is_active == True
        )
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    return patient


# =====================================
# 4. UPDATE PATIENT
# =====================================

@router.put(
    "/{patient_id}",
    response_model=PatientResponse
)
def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    patient = db.scalar(
        select(Patient).where(
            Patient.patient_id == patient_id,
            Patient.organization_id == current_user.organization_id,
            Patient.is_active == True
        )
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    update_data = patient_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(patient, field, value)

    create_audit_log(
        db=db,
        organization_id=current_user.organization_id,
        actor_user_id=current_user.user_id,
        action="PATIENT_UPDATED",
        entity_type="PATIENT",
        entity_id=patient.patient_id,
        details={
            "updated_fields": list(update_data.keys())
        }
    )

    db.commit()
    db.refresh(patient)

    return patient


# =====================================
# 5. DEACTIVATE PATIENT
# =====================================

@router.delete(
    "/{patient_id}"
)
def deactivate_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    patient = db.scalar(
        select(Patient).where(
            Patient.patient_id == patient_id,
            Patient.organization_id == current_user.organization_id,
            Patient.is_active == True
        )
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    patient.is_active = False

    create_audit_log(
        db=db,
        organization_id=current_user.organization_id,
        actor_user_id=current_user.user_id,
        action="PATIENT_DEACTIVATED",
        entity_type="PATIENT",
        entity_id=patient.patient_id,
        details={
            "patient_name": patient.patient_name
        }
    )

    db.commit()

    return {
        "message": "Patient deactivated successfully",
        "patient_id": patient.patient_id
    }
