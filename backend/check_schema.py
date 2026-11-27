
from sqlalchemy import inspect

from app.database import engine
from app.models import (
    Organization,
    User,
    Patient,
    Appointment,
    CareInstruction,
    Reminder,
    AuditLog
)

# All registered SQLAlchemy models
models = [
    Organization,
    User,
    Patient,
    Appointment,
    CareInstruction,
    Reminder,
    AuditLog
]

# Inspect actual MySQL database
inspector = inspect(engine)

print("\n========== DATABASE SCHEMA VALIDATION ==========\n")

database_tables = set(inspector.get_table_names())

all_passed = True

for model in models:

    table_name = model.__tablename__

    print(f"\nChecking table: {table_name}")

    # Check whether table exists
    if table_name not in database_tables:
        print("FAILED: Table does not exist in MySQL")
        all_passed = False
        continue

    # Get actual MySQL columns
    db_columns = {
        column["name"]
        for column in inspector.get_columns(table_name)
    }

    # Get Python model columns
    model_columns = set(model.__table__.columns.keys())

    missing_columns = model_columns - db_columns
    extra_columns = db_columns - model_columns

    if not missing_columns and not extra_columns:
        print("PASSED: All columns match")
    else:
        all_passed = False

        if missing_columns:
            print("Missing in MySQL:", missing_columns)

        if extra_columns:
            print("Extra in MySQL:", extra_columns)

print("\n==============================================")

if all_passed:
    print("SUCCESS: ALL SEVEN TABLES VERIFIED")
else:
    print("WARNING: SCHEMA MISMATCH FOUND")

engine.dispose()
