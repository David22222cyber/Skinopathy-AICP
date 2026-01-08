import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy import create_engine, MetaData, Table, select

# --------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------
# Adjust this to your environment
DB_URL = (
    "mssql+pyodbc://username:password"
    "@skinopathy.database.windows.net"
    "/AICP_Database"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&Encrypt=yes"
    "&TrustServerCertificate=yes"
)


NUM_DOCTORS = 15
NUM_PHARMACIES = 10
NUM_PATIENTS = 50

# how many rows for each child table (per patient or total)
PER_PATIENT = {
    "referral_logs": (0, 2),              # min, max per patient
    "appointments": (0, 4),
    "patient_contacts": (0, 2),
    "document_filled_out": (0, 2),
    "patient_identity_verification": (0, 1),
    "patient_lesion_history": (0, 3),
    "patient_notes": (0, 3),
    "promo_codes": (0, 1),
    "task_notes": (0, 2),
    "uploaded_documents": (0, 2),
    "walkin_cases": (0, 2),
    "patient_last_measurement": (0, 1),
    "bills": (0, 3),
    "patient_history": (0, 3),
    "submissions": (0, 3),
}

# --------------------------------------------------------------------
# SETUP
# --------------------------------------------------------------------
fake = Faker()
random.seed(42)
Faker.seed(42)

engine = create_engine(DB_URL)
metadata = MetaData()

# reflect the tables we care about (schema dbo)
address_book_doctors = Table(
    "address_book_doctors", metadata, schema="dbo", autoload_with=engine
)
pharmacies = Table(
    "pharmacies", metadata, schema="dbo", autoload_with=engine
)
patients = Table(
    "patients", metadata, schema="dbo", autoload_with=engine
)
referral_logs = Table(
    "referral_logs", metadata, schema="dbo", autoload_with=engine
)
appointments = Table(
    "appointments", metadata, schema="dbo", autoload_with=engine
)
patient_contacts = Table(
    "patient_contacts", metadata, schema="dbo", autoload_with=engine
)
document_filled_out = Table(
    "document_filled_out", metadata, schema="dbo", autoload_with=engine
)
patient_identity_verification = Table(
    "patient_identity_verification", metadata, schema="dbo", autoload_with=engine
)
patient_lesion_history = Table(
    "patient_lesion_history", metadata, schema="dbo", autoload_with=engine
)
patient_notes = Table(
    "patient_notes", metadata, schema="dbo", autoload_with=engine
)
promo_codes = Table(
    "promo_codes", metadata, schema="dbo", autoload_with=engine
)
task_notes = Table(
    "task_notes", metadata, schema="dbo", autoload_with=engine
)
uploaded_documents = Table(
    "uploaded_documents", metadata, schema="dbo", autoload_with=engine
)
walkin_cases = Table(
    "walkin_cases", metadata, schema="dbo", autoload_with=engine
)
patient_last_measurement = Table(
    "patient_last_measurement", metadata, schema="dbo", autoload_with=engine
)
bills = Table(
    "bills", metadata, schema="dbo", autoload_with=engine
)
patient_history = Table(
    "patient_history", metadata, schema="dbo", autoload_with=engine
)
submissions = Table(
    "submissions", metadata, schema="dbo", autoload_with=engine
)

# --------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------
def random_bool(p_true=0.5):
    return random.random() < p_true


def random_datetime_within(days_back=365):
    now = datetime.utcnow()
    delta = timedelta(days=random.randint(0, days_back), seconds=random.randint(0, 86400))
    return now - delta


def per_patient_count(table_name):
    lo, hi = PER_PATIENT.get(table_name, (0, 0))
    if hi <= 0:
        return 0
    return random.randint(lo, hi)


# --------------------------------------------------------------------
# SEED FUNCTIONS
# --------------------------------------------------------------------
def seed_doctors(conn, n=NUM_DOCTORS):
    rows = []
    for _ in range(n):
        first = fake.first_name()
        last = fake.last_name()
        rows.append(
            {
                "cpso_number": str(fake.random_int(100000, 999999)),
                "first_name": first,
                "last_name": last,
                "clinic_name": f"{last} Dermatology Clinic",
                "clinic_address": fake.street_address(),
                "clinic_address_2": None,
                "city": fake.city(),
                "province": "ON",
                "postal": fake.postalcode(),
                "phone": fake.phone_number(),
                "fax": fake.phone_number(),
                "email": fake.email(),
                "status": random.choice(["active", "inactive"]),
                "notes": fake.text(max_nb_chars=100),
                "for_search": None,
                "for_search_vector": None,
            }
        )
    conn.execute(address_book_doctors.insert(), rows)
    doctor_ids = conn.execute(select(address_book_doctors.c.id)).scalars().all()
    return doctor_ids


def seed_pharmacies(conn, n=NUM_PHARMACIES):
    rows = []
    for _ in range(n):
        rows.append(
            {
                "name": f"{fake.company()} Pharmacy",
                "store_number": str(fake.random_int(100, 999)),
                "street_address": fake.street_address(),
                "street_address_2": None,
                "city": fake.city(),
                "province": "ON",
                "postal": fake.postalcode(),
                "phone": fake.phone_number(),
                "fax": fake.phone_number(),
                "email": fake.email(),
                "status": random.choice(["active", "inactive"]),
                "notes": fake.text(max_nb_chars=100),
                "for_search": None,
                "for_search_vector": None,
            }
        )
    conn.execute(pharmacies.insert(), rows)
    pharmacy_ids = conn.execute(select(pharmacies.c.id)).scalars().all()
    return pharmacy_ids


def seed_patients(conn, doctor_ids, pharmacy_ids, n=NUM_PATIENTS):
    rows = []
    for _ in range(n):
        first = fake.first_name()
        last = fake.last_name()
        birth = fake.date_of_birth(minimum_age=18, maximum_age=95)
        fam_dr = random.choice(doctor_ids) if doctor_ids and random_bool(0.7) else None
        ref_dr = random.choice(doctor_ids) if doctor_ids and random_bool(0.4) else None
        pharm = random.choice(pharmacy_ids) if pharmacy_ids and random_bool(0.7) else None

        rows.append(
            {
                "first_name": first,
                "last_name": last,
                "birth": birth,
                "sex": random.choice(["male", "female", "other"]),
                "street_address": fake.street_address(),
                "street_address_2": None,
                "city": fake.city(),
                "province": "ON",
                "postal": fake.postalcode(),
                "health_card_number": str(fake.random_int(1000000000, 9999999999)),
                "health_card_expiry_date": birth.replace(year=birth.year + 70),
                "home_phone": fake.phone_number(),
                "cell_phone": fake.phone_number(),
                "email": fake.email(),
                "created_at": random_datetime_within(365),
                "creator_id": None,
                "family_dr_id": fam_dr,
                "referring_dr_id": ref_dr,
                "global_message": None,
                "from_app": random_bool(0.3),
                "medical_history": fake.text(max_nb_chars=200),
                "allergy_history": fake.text(max_nb_chars=100),
                "medication_history": fake.text(max_nb_chars=150),
                "pharmacy_id": pharm,
                "app_uid": None,
                "insurer": random.choice(["OHIP", "Private", "Uninsured"]),
                "app_token": None,
                "privacy_consent": random_bool(0.95),
                "medical_data_consent": random_bool(0.95),
                "family_practice_notification_status": random.choice(
                    [None, "pending", "sent", "acknowledged"]
                ),
                "insurance_status": random.choice(
                    ["valid", "expired", "pending", None]
                ),
                "pharmacy_delivery_status": random.choice(
                    [None, "enabled", "disabled"]
                ),
                "archived": random_bool(0.05),
                "ekg_larm_patient_id": None,
                "ekg_larm_patient_hash": None,
                "mailing_location_id": None,
                "mailings_dr_location_id": None,
                "previous_specialist_id": None,
                "previous_specialist_location_id": None,
                "preferred_patient_contact_id": None,
                "is_contact": random_bool(0.1),
                "health_card_valid": random_bool(0.9),
                "health_card_last_validated": random_datetime_within(365),
                "has_different_mailing_address": random_bool(0.1),
                "preferred_name": first if random_bool(0.8) else fake.first_name(),
                "preferred_contact_method": random.choice(
                    [None, "phone", "email", "text"]
                ),
                "con_call": random_bool(0.7),
                "con_email": random_bool(0.7),
                "con_text": random_bool(0.7),
                "english_marketing_consent": random_bool(0.5),
                "third_party_research_consent": random_bool(0.3),
                "emr_uid": None,
                "patient_uid": None,
                "phil_marketing_consent": random_bool(0.3),
                "sms_email_consent_verification_attempts": random.randint(0, 3),
                "acu_id": None,
                "mailing_address": None,
                "for_search": None,
                "for_search_roman": None,
                "for_search_jpn_goo": None,
                "workbase_school": None,
                "for_search_kana": None,
                "government_id": None,
                "for_search_vector": None,
                "tax_number": str(fake.random_int(100000000, 999999999)),
                "medical_name": f"{last}, {first}",
            }
        )

    conn.execute(patients.insert(), rows)
    patient_ids = conn.execute(select(patients.c.id)).scalars().all()
    return patient_ids


# --------------------------------------------------------------------
# CHILD TABLES (ALL REQUIRE patient_id)
# --------------------------------------------------------------------
def seed_referral_logs(conn, patient_ids, doctor_ids, pharmacy_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("referral_logs")):
            rows.append(
                {
                    "patient_id": pid,
                    "referring_dr_id": random.choice(doctor_ids) if doctor_ids else None,
                    "pharmacy_id": random.choice(pharmacy_ids) if pharmacy_ids else None,
                    "created_at": random_datetime_within(365),
                    "archived": random_bool(0.1),
                    "notes": fake.text(max_nb_chars=120),
                }
            )
    if rows:
        conn.execute(referral_logs.insert(), rows)


def seed_appointments(conn, patient_ids, doctor_ids, pharmacy_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("appointments")):
            start = random_datetime_within(365)
            end = start + timedelta(minutes=random.choice([15, 30, 45]))
            rows.append(
                {
                    "appointment_uid": fake.uuid4(),
                    "patient_id": pid,
                    "doctor_id": random.choice(doctor_ids) if doctor_ids else None,
                    "start_time": start,
                    "end_time": end,
                    "status": random.choice(["booked", "completed", "cancelled"]),
                    "visit_type": random.choice(["initial", "follow-up", "walk-in"]),
                    "created_at": start - timedelta(days=7),
                    "created_by": None,
                    "updated_at": end,
                    "updated_by": None,
                    "notes": fake.text(max_nb_chars=80),
                    "pharmacy_id": random.choice(pharmacy_ids) if pharmacy_ids else None,
                }
            )
    if rows:
        conn.execute(appointments.insert(), rows)


def seed_patient_contacts(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("patient_contacts")):
            rows.append(
                {
                    "patient_id": pid,
                    "contact_id": None,  # could point to another patient if you want
                    "relationship": random.choice(
                        ["spouse", "parent", "child", "friend", "caregiver"]
                    ),
                    "preferred_contact_method": random.choice(
                        ["phone", "email", "text"]
                    ),
                }
            )
    if rows:
        conn.execute(patient_contacts.insert(), rows)


def seed_document_filled_out(conn, patient_ids, doctor_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("document_filled_out")):
            rows.append(
                {
                    "template_id": random.randint(1, 5),
                    "patient_id": pid,
                    "doctor_id": random.choice(doctor_ids) if doctor_ids else None,
                    "date_filled": random_datetime_within(365),
                    "data_json": '{"field1":"value1","field2":"value2"}',
                    "notes": fake.text(max_nb_chars=80),
                    "archived": random_bool(0.1),
                }
            )
    if rows:
        conn.execute(document_filled_out.insert(), rows)


def seed_patient_identity_verification(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("patient_identity_verification")):
            rows.append(
                {
                    "patient_id": pid,
                    "method": random.choice(["sms", "email", "id_check"]),
                    "verified_at": random_datetime_within(365),
                    "status": random.choice(["verified", "failed", "pending"]),
                    "notes": fake.text(max_nb_chars=80),
                }
            )
    if rows:
        conn.execute(patient_identity_verification.insert(), rows)


def seed_patient_lesion_history(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("patient_lesion_history")):
            rows.append(
                {
                    "patient_id": pid,
                    "image_urls": "https://example.com/image1.jpg",
                    "body_area": random.choice(
                        ["face", "arm", "leg", "torso", "back", "scalp"]
                    ),
                    "is_facing_forward": random_bool(0.5),
                    "x_location": random.randint(0, 1000),
                    "y_location": random.randint(0, 1000),
                    "questionnaire_data": '{"q1":"yes","q2":"no"}',
                    "review_status": random.choice(
                        ["pending", "reviewed", "needs_follow_up"]
                    ),
                    "date_examined": random_datetime_within(365),
                    "ai_analysis": "low risk",
                    "doctor_analysis": "monitor",
                    "admin_comments": None,
                    "lesion_uid": fake.uuid4(),
                    "is_ai_correct": random_bool(0.8),
                    "urgency_rating": random.randint(1, 5),
                    "user_accepted_review": random_bool(0.9),
                }
            )
    if rows:
        conn.execute(patient_lesion_history.insert(), rows)


def seed_patient_notes(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("patient_notes")):
            rows.append(
                {
                    "patient_id": pid,
                    "note": fake.paragraph(nb_sentences=3),
                    "created_at": random_datetime_within(365),
                    "created_by": None,
                }
            )
    if rows:
        conn.execute(patient_notes.insert(), rows)


def seed_promo_codes(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("promo_codes")):
            code = fake.bothify(text="PROMO-####")
            start = fake.date_between(start_date="-1y", end_date="today")
            end = start + timedelta(days=random.randint(7, 60))
            rows.append(
                {
                    "code": code,
                    "patient_id": pid,
                    "start_date": start,
                    "end_date": end,
                    "notes": fake.text(max_nb_chars=60),
                    "archived": random_bool(0.2),
                }
            )
    if rows:
        conn.execute(promo_codes.insert(), rows)


def seed_task_notes(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("task_notes")):
            rows.append(
                {
                    "patient_id": pid,
                    "title": fake.sentence(nb_words=6),
                    "note": fake.paragraph(nb_sentences=2),
                    "created_at": random_datetime_within(365),
                    "created_by": None,
                    "completed": random_bool(0.5),
                }
            )
    if rows:
        conn.execute(task_notes.insert(), rows)


def seed_uploaded_documents(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("uploaded_documents")):
            rows.append(
                {
                    "patient_id": pid,
                    "title": fake.sentence(nb_words=4),
                    "file_name": fake.file_name(extension="pdf"),
                    "mime_type": "application/pdf",
                    "size_bytes": random.randint(10_000, 300_000),
                    "uploaded_at": random_datetime_within(365),
                    "uploaded_by": None,
                    "archived": random_bool(0.2),
                }
            )
    if rows:
        conn.execute(uploaded_documents.insert(), rows)


def seed_walkin_cases(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("walkin_cases")):
            rows.append(
                {
                    "patient_id": pid,
                    "created_at": random_datetime_within(365),
                    "status": random.choice(
                        ["open", "in_progress", "closed", "cancelled"]
                    ),
                    "notes": fake.paragraph(nb_sentences=2),
                }
            )
    if rows:
        conn.execute(walkin_cases.insert(), rows)


def seed_patient_last_measurement(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("patient_last_measurement")):
            rows.append(
                {
                    "patient_id": pid,
                    "height_cm": round(random.uniform(150, 195), 1),
                    "weight_kg": round(random.uniform(50, 110), 1),
                    "blood_pressure": f"{random.randint(100, 150)}/{random.randint(60, 95)}",
                    "pulse": random.randint(55, 110),
                    "measured_at": random_datetime_within(365),
                    "measured_by": None,
                }
            )
    if rows:
        conn.execute(patient_last_measurement.insert(), rows)


def seed_bills(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("bills")):
            amount = round(random.uniform(50, 400), 2)
            issued = random_datetime_within(365)
            paid = issued + timedelta(days=random.randint(0, 60)) if random_bool(0.7) else None
            status = "paid" if paid else random.choice(["unpaid", "cancelled"])
            rows.append(
                {
                    "patient_id": pid,
                    "visit_number": fake.bothify(text="VIS-#####"),
                    "invoice_number": fake.bothify(text="INV-#####"),
                    "amount": amount,
                    "issued_at": issued,
                    "paid_at": paid,
                    "status": status,
                    "notes": fake.text(max_nb_chars=80),
                }
            )
    if rows:
        conn.execute(bills.insert(), rows)


def seed_patient_history(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("patient_history")):
            rows.append(
                {
                    "patient_id": pid,
                    "change_type": random.choice(
                        ["create", "update", "archive", "merge"]
                    ),
                    "change_details": '{"field":"value_before->value_after"}',
                    "changed_by": random.choice(["system", "admin", "staff"]),
                    # changed_at has default, but we can explicitly set as well
                    "changed_at": random_datetime_within(365),
                }
            )
    if rows:
        conn.execute(patient_history.insert(), rows)


def seed_submissions(conn, patient_ids):
    rows = []
    for pid in patient_ids:
        for _ in range(per_patient_count("submissions")):
            rows.append(
                {
                    "patient_id": pid,
                    "submission_type": random.choice(
                        ["intake_form", "questionnaire", "followup_form"]
                    ),
                    "submitted_at": random_datetime_within(365),
                    "submitted_by": random.choice(["patient", "staff", "app"]),
                    "status": random.choice(["pending", "reviewed", "archived"]),
                    "payload": '{"q1":"yes","q2":"no"}',
                    "notes": fake.text(max_nb_chars=80),
                }
            )
    if rows:
        conn.execute(submissions.insert(), rows)


# --------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------
def main():
    with engine.begin() as conn:
        print("Seeding doctors...")
        doctor_ids = seed_doctors(conn)

        print("Seeding pharmacies...")
        pharmacy_ids = seed_pharmacies(conn)

        print("Seeding patients...")
        patient_ids = seed_patients(conn, doctor_ids, pharmacy_ids)

        print("Seeding dependent tables...")
        seed_referral_logs(conn, patient_ids, doctor_ids, pharmacy_ids)
        seed_appointments(conn, patient_ids, doctor_ids, pharmacy_ids)
        seed_patient_contacts(conn, patient_ids)
        seed_document_filled_out(conn, patient_ids, doctor_ids)
        seed_patient_identity_verification(conn, patient_ids)
        seed_patient_lesion_history(conn, patient_ids)
        seed_patient_notes(conn, patient_ids)
        seed_promo_codes(conn, patient_ids)
        seed_task_notes(conn, patient_ids)
        seed_uploaded_documents(conn, patient_ids)
        seed_walkin_cases(conn, patient_ids)
        seed_patient_last_measurement(conn, patient_ids)
        seed_bills(conn, patient_ids)
        seed_patient_history(conn, patient_ids)
        seed_submissions(conn, patient_ids)

        print("Done!")


if __name__ == "__main__":
    main()
