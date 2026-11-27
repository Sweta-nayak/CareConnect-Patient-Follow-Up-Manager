
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_roles
from app.models import CareInstruction, Patient, User

from app.schemas.care_instruction import (
    CareInstructionCreate,
    CareInstructionUpdate,
    CareInstructionResponse
)


router = APIRouter(
    prefix="/api/care-instructions",
    tags=["Care Instructions"]
)


# =========================================
# VALIDATE PATIENT
# =========================================

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
            detail="Active patient not found in your organization"
        )

    return patient


# =========================================
# VALIDATE DOCTOR
# =========================================

def validate_doctor(
    db: Session,
    clinician_user_id: str,
    organization_id: str
):
    doctor = db.scalar(
        select(User).where(
            User.user_id == clinician_user_id,
            User.organization_id == organization_id,
            User.role == "DOCTOR",
            User.is_active == True
        )
    )

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active doctor not found in your organization"
        )

    return doctor


# =========================================
# 1. CREATE CARE INSTRUCTION
# ADMIN AND DOCTOR
# =========================================

@router.post(
    "/",
    response_model=CareInstructionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_care_instruction(
    data: CareInstructionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DOCTOR")
    )
):

    validate_patient(
        db,
        data.patient_id,
        current_user.organization_id
    )

    validate_doctor(
        db,
        data.clinician_user_id,
        current_user.organization_id
    )

    new_instruction = CareInstruction(
        organization_id=current_user.organization_id,
        patient_id=data.patient_id,
        clinician_user_id=data.clinician_user_id,
        instruction_type=data.instruction_type,
        instruction_text=data.instruction_text,
        start_date=data.start_date,
        end_date=data.end_date,
        approval_status="DRAFT"
    )

    db.add(new_instruction)
    db.commit()
    db.refresh(new_instruction)

    return new_instruction


# =========================================
# 2. GET ALL CARE INSTRUCTIONS
# =========================================

@router.get(
    "/",
    response_model=list[CareInstructionResponse]
)
def get_care_instructions(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DOCTOR", "RECEPTIONIST")
    )
):

    instructions = db.scalars(
        select(CareInstruction).where(
            CareInstruction.organization_id
            == current_user.organization_id
        ).order_by(CareInstruction.created_at.desc())
    ).all()

    return instructions


# =========================================
# 3. GET ONE CARE INSTRUCTION
# =========================================

@router.get(
    "/{instruction_id}",
    response_model=CareInstructionResponse
)
def get_care_instruction(
    instruction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DOCTOR", "RECEPTIONIST")
    )
):

    instruction = db.scalar(
        select(CareInstruction).where(
            CareInstruction.instruction_id == instruction_id,
            CareInstruction.organization_id
            == current_user.organization_id
        )
    )

    if not instruction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Care instruction not found"
        )

    return instruction


# =========================================
# 4. UPDATE CARE INSTRUCTION
# ADMIN AND DOCTOR
# =========================================

@router.put(
    "/{instruction_id}",
    response_model=CareInstructionResponse
)
def update_care_instruction(
    instruction_id: str,
    data: CareInstructionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DOCTOR")
    )
):

    instruction = db.scalar(
        select(CareInstruction).where(
            CareInstruction.instruction_id == instruction_id,
            CareInstruction.organization_id
            == current_user.organization_id
        )
    )

    if not instruction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Care instruction not found"
        )

    if instruction.approval_status != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft instructions can be updated"
        )

    update_data = data.model_dump(exclude_unset=True)

    new_start = update_data.get(
        "start_date",
        instruction.start_date
    )

    new_end = update_data.get(
        "end_date",
        instruction.end_date
    )

    if new_start and new_end and new_end < new_start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="End date cannot be earlier than start date"
        )

    for key, value in update_data.items():
        setattr(instruction, key, value)

    db.commit()
    db.refresh(instruction)

    return instruction


# =========================================
# 5. APPROVE CARE INSTRUCTION
# ADMIN AND DOCTOR
# =========================================

@router.patch(
    "/{instruction_id}/approve",
    response_model=CareInstructionResponse
)
def approve_care_instruction(
    instruction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DOCTOR")
    )
):

    instruction = db.scalar(
        select(CareInstruction).where(
            CareInstruction.instruction_id == instruction_id,
            CareInstruction.organization_id
            == current_user.organization_id
        )
    )

    if not instruction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Care instruction not found"
        )

    if instruction.approval_status != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft instructions can be approved"
        )

    instruction.approval_status = "APPROVED"
    instruction.approved_at = datetime.now(timezone.utc).replace(
        tzinfo=None
    )

    db.commit()
    db.refresh(instruction)

    return instruction


# =========================================
# 6. CANCEL CARE INSTRUCTION
# ADMIN AND DOCTOR
# =========================================

@router.patch(
    "/{instruction_id}/cancel",
    response_model=CareInstructionResponse
)
def cancel_care_instruction(
    instruction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "DOCTOR")
    )
):

    instruction = db.scalar(
        select(CareInstruction).where(
            CareInstruction.instruction_id == instruction_id,
            CareInstruction.organization_id
            == current_user.organization_id
        )
    )

    if not instruction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Care instruction not found"
        )

    if instruction.approval_status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instruction is already cancelled"
        )

    instruction.approval_status = "CANCELLED"

    db.commit()
    db.refresh(instruction)

    return instruction
