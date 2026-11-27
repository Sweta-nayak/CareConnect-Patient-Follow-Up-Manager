-- =========================================
-- TABLE 1: ORGANIZATIONS
-- =========================================

CREATE TABLE IF NOT EXISTS organizations (

    organization_id CHAR(36) PRIMARY KEY,

    organization_name VARCHAR(100) NOT NULL,

    organization_code VARCHAR(50) NOT NULL UNIQUE,

    is_active BOOLEAN DEFAULT TRUE,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================
-- TABLE 2: USERS
-- =========================================

CREATE TABLE IF NOT EXISTS users (

    user_id CHAR(36) PRIMARY KEY,

    organization_id CHAR(36) NOT NULL,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(50) NOT NULL,

    password_hash VARCHAR(255) NOT NULL,

    role ENUM('ADMIN', 'DOCTOR', 'RECEPTIONIST') NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_user_org_email (organization_id, email),

    UNIQUE KEY uq_user_org_id (organization_id, user_id),

    CONSTRAINT fk_users_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations(organization_id)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================
-- TABLE 3: PATIENTS
-- =========================================

CREATE TABLE IF NOT EXISTS patients (

    patient_id CHAR(36) PRIMARY KEY,

    organization_id CHAR(36) NOT NULL,

    patient_name VARCHAR(100) NOT NULL,

    date_of_birth DATE,

    gender VARCHAR(20),

    phone_number VARCHAR(20) NOT NULL,

    email VARCHAR(150),

    consent_sms BOOLEAN DEFAULT FALSE,

    consent_whatsapp BOOLEAN DEFAULT FALSE,

    is_active BOOLEAN DEFAULT TRUE,

    created_by CHAR(36),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_patient_org_id (organization_id, patient_id),

    CONSTRAINT fk_patients_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations(organization_id),

    CONSTRAINT fk_patients_creator
        FOREIGN KEY (organization_id, created_by)
        REFERENCES users(organization_id, user_id)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================
-- TABLE 4: APPOINTMENTS
-- =========================================

CREATE TABLE IF NOT EXISTS appointments (

    appointment_id CHAR(36) PRIMARY KEY,

    organization_id CHAR(36) NOT NULL,

    patient_id CHAR(36) NOT NULL,

    clinician_user_id CHAR(36) NOT NULL,

    appointment_datetime DATETIME NOT NULL,

    appointment_type VARCHAR(50),

    status ENUM(
        'SCHEDULED',
        'CONFIRMED',
        'ATTENDED',
        'MISSED',
        'RESCHEDULED',
        'CANCELLED'
    ) DEFAULT 'SCHEDULED',

    reason VARCHAR(255),

    notes TEXT,

    created_by CHAR(36),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY uq_appointment_org_id
    (organization_id, appointment_id),

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_appointment_patient
        FOREIGN KEY (organization_id, patient_id)
        REFERENCES patients(organization_id, patient_id),

    CONSTRAINT fk_appointment_clinician
        FOREIGN KEY (organization_id, clinician_user_id)
        REFERENCES users(organization_id, user_id),

    CONSTRAINT fk_appointment_creator
        FOREIGN KEY (organization_id, created_by)
        REFERENCES users(organization_id, user_id),

    INDEX idx_appointment_schedule (organization_id, appointment_datetime),

    INDEX idx_appointment_status (organization_id, status)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================
-- TABLE 5: CARE INSTRUCTIONS
-- =========================================

CREATE TABLE IF NOT EXISTS care_instructions (

    instruction_id CHAR(36) PRIMARY KEY,

    organization_id CHAR(36) NOT NULL,

    patient_id CHAR(36) NOT NULL,

    clinician_user_id CHAR(36) NOT NULL,

    instruction_type ENUM(
        'MEDICINE',
        'TEST',
        'CONSULTATION'
    ) NOT NULL,

    instruction_text TEXT NOT NULL,

    start_date DATE,

    end_date DATE,

    approval_status ENUM(
        'DRAFT',
        'APPROVED',
        'CANCELLED'
    ) DEFAULT 'DRAFT',

    approved_at DATETIME,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY uq_instruction_org_id
    (organization_id, instruction_id),

    CONSTRAINT fk_instruction_patient
        FOREIGN KEY (organization_id, patient_id)
        REFERENCES patients(organization_id, patient_id),

    CONSTRAINT fk_instruction_clinician
        FOREIGN KEY (organization_id, clinician_user_id)
        REFERENCES users(organization_id, user_id),

    INDEX idx_instruction_patient (organization_id, patient_id)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================
-- TABLE 6: REMINDERS
-- =========================================

CREATE TABLE IF NOT EXISTS reminders (

    reminder_id CHAR(36) PRIMARY KEY,

    organization_id CHAR(36) NOT NULL,

    patient_id CHAR(36) NOT NULL,

    instruction_id CHAR(36),

    appointment_id CHAR(36),

    channel ENUM('SMS', 'WHATSAPP') NOT NULL,

    reminder_type ENUM(
        'APPOINTMENT',
        'MEDICINE',
        'TEST',
        'CONSULTATION'
    ) NOT NULL,

    scheduled_at DATETIME NOT NULL,

    message_text TEXT NOT NULL,

    status ENUM(
        'PENDING',
        'SIMULATED',
        'SENT',
        'FAILED',
        'CANCELLED'
    ) DEFAULT 'PENDING',

    idempotency_key VARCHAR(150) NOT NULL,

    attempted_at DATETIME,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    

    UNIQUE KEY uq_reminder_idempotency (organization_id, idempotency_key),

    CONSTRAINT fk_reminder_patient
        FOREIGN KEY (organization_id, patient_id)
        REFERENCES patients(organization_id, patient_id),

    CONSTRAINT fk_reminder_instruction
        FOREIGN KEY (organization_id, instruction_id)
        REFERENCES care_instructions(organization_id, instruction_id),

    CONSTRAINT fk_reminder_appointment
        FOREIGN KEY (organization_id, appointment_id)
        REFERENCES appointments(organization_id, appointment_id),

    INDEX idx_reminder_schedule (organization_id, scheduled_at, status)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================
-- TABLE 7: AUDIT LOGS
-- =========================================

CREATE TABLE IF NOT EXISTS audit_logs (

    audit_id CHAR(36) PRIMARY KEY,

    organization_id CHAR(36) NOT NULL,

    actor_user_id CHAR(36),

    action VARCHAR(100) NOT NULL,

    entity_type VARCHAR(100),

    entity_id CHAR(36),

    details JSON,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_organization
        FOREIGN KEY (organization_id)
        REFERENCES organizations(organization_id),

    CONSTRAINT fk_audit_user
        FOREIGN KEY (organization_id, actor_user_id)
        REFERENCES users(organization_id, user_id),

    INDEX idx_audit_org_date (organization_id, created_at)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
