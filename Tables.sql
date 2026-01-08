------------------------------------------------------------
-- 1) Doctors (address book)
------------------------------------------------------------
CREATE TABLE dbo.address_book_doctors (
    id                  INT IDENTITY(1,1) PRIMARY KEY,
    cpso_number         NVARCHAR(50)     NULL,
    first_name          NVARCHAR(100)    NULL,
    last_name           NVARCHAR(100)    NULL,
    clinic_name         NVARCHAR(255)    NULL,
    clinic_address      NVARCHAR(255)    NULL,
    clinic_address_2    NVARCHAR(255)    NULL,
    city                NVARCHAR(100)    NULL,
    province            NVARCHAR(100)    NULL,
    postal              NVARCHAR(20)     NULL,
    phone               NVARCHAR(30)     NULL,
    fax                 NVARCHAR(30)     NULL,
    email               NVARCHAR(255)    NULL,
    status              NVARCHAR(50)     NULL,
    notes               NVARCHAR(MAX)    NULL,
    for_search          NVARCHAR(MAX)    NULL,
    for_search_vector   NVARCHAR(MAX)    NULL -- SQL Server doesn't have tsvector
);
GO

------------------------------------------------------------
-- 2) Pharmacies
------------------------------------------------------------
CREATE TABLE dbo.pharmacies (
    id                  INT IDENTITY(1,1) PRIMARY KEY,
    name                NVARCHAR(255)    NULL,
    store_number        NVARCHAR(50)     NULL,
    street_address      NVARCHAR(255)    NULL,
    street_address_2    NVARCHAR(255)    NULL,
    city                NVARCHAR(100)    NULL,
    province            NVARCHAR(100)    NULL,
    postal              NVARCHAR(20)     NULL,
    phone               NVARCHAR(30)     NULL,
    fax                 NVARCHAR(30)     NULL,
    email               NVARCHAR(255)    NULL,
    status              NVARCHAR(50)     NULL,
    notes               NVARCHAR(MAX)    NULL,
    for_search          NVARCHAR(MAX)    NULL,
    for_search_vector   NVARCHAR(MAX)    NULL
);
GO

------------------------------------------------------------
-- 3) Patients (central table)
------------------------------------------------------------
CREATE TABLE dbo.patients (
    id                                  INT IDENTITY(1,1) PRIMARY KEY,
    first_name                          NVARCHAR(100)    NULL,
    last_name                           NVARCHAR(100)    NULL,
    birth                               DATE             NULL,
    sex                                 NVARCHAR(20)     NULL,
    street_address                      NVARCHAR(255)    NULL,
    street_address_2                    NVARCHAR(255)    NULL,
    city                                NVARCHAR(100)    NULL,
    province                            NVARCHAR(100)    NULL,
    postal                              NVARCHAR(20)     NULL,
    health_card_number                  NVARCHAR(50)     NULL,
    health_card_expiry_date             DATE             NULL,
    home_phone                          NVARCHAR(30)     NULL,
    cell_phone                          NVARCHAR(30)     NULL,
    email                               NVARCHAR(255)    NULL,
    created_at                          DATETIME2        NULL,
    creator_id                          INT              NULL,
    family_dr_id                        INT              NULL,
    referring_dr_id                     INT              NULL,
    global_message                      NVARCHAR(MAX)    NULL,
    from_app                            BIT              NULL,
    medical_history                     NVARCHAR(MAX)    NULL,
    allergy_history                     NVARCHAR(MAX)    NULL,
    medication_history                  NVARCHAR(MAX)    NULL,
    pharmacy_id                         INT              NULL,
    app_uid                             NVARCHAR(255)    NULL,
    insurer                             NVARCHAR(100)    NULL,
    app_token                           NVARCHAR(255)    NULL,
    privacy_consent                     BIT              NULL,
    medical_data_consent                BIT              NULL,
    family_practice_notification_status NVARCHAR(50)     NULL,
    insurance_status                    NVARCHAR(50)     NULL,
    pharmacy_delivery_status            NVARCHAR(50)     NULL,
    archived                            BIT              NULL,
    ekg_larm_patient_id                 INT              NULL,
    ekg_larm_patient_hash               NVARCHAR(255)    NULL,
    mailing_location_id                 INT              NULL,
    mailings_dr_location_id             INT              NULL,
    previous_specialist_id              INT              NULL,
    previous_specialist_location_id     INT              NULL,
    preferred_patient_contact_id        INT              NULL,
    is_contact                          BIT              NULL,
    health_card_valid                   BIT              NULL,
    health_card_last_validated          DATETIME2        NULL,
    has_different_mailing_address       BIT              NULL,
    preferred_name                      NVARCHAR(100)    NULL,
    preferred_contact_method            NVARCHAR(50)     NULL,
    con_call                            BIT              NULL,
    con_email                           BIT              NULL,
    con_text                            BIT              NULL,
    english_marketing_consent           BIT              NULL,
    third_party_research_consent        BIT              NULL,
    emr_uid                             NVARCHAR(255)    NULL,
    patient_uid                         NVARCHAR(255)    NULL,
    phil_marketing_consent              BIT              NULL,
    sms_email_consent_verification_attempts INT          NULL,
    acu_id                              INT              NULL,
    mailing_address                     NVARCHAR(MAX)    NULL,
    for_search                          NVARCHAR(MAX)    NULL,
    for_search_roman                    NVARCHAR(MAX)    NULL,
    for_search_jpn_goo                  NVARCHAR(MAX)    NULL,
    workbase_school                     NVARCHAR(MAX)    NULL,
    for_search_kana                     NVARCHAR(MAX)    NULL,
    government_id                       NVARCHAR(255)    NULL,
    for_search_vector                   NVARCHAR(MAX)    NULL,
    tax_number                          NVARCHAR(50)     NULL,
    medical_name                        NVARCHAR(255)    NULL,
    CONSTRAINT fk_patients_pharmacy
        FOREIGN KEY (pharmacy_id) REFERENCES dbo.pharmacies(id),
    CONSTRAINT fk_patients_referring_dr
        FOREIGN KEY (referring_dr_id) REFERENCES dbo.address_book_doctors(id),
    CONSTRAINT fk_patients_family_dr
        FOREIGN KEY (family_dr_id) REFERENCES dbo.address_book_doctors(id)
);
GO

------------------------------------------------------------
-- 4) Referral logs (top-left box)
------------------------------------------------------------
CREATE TABLE dbo.referral_logs (
    id                      INT IDENTITY(1,1) PRIMARY KEY,
    patient_id              INT          NOT NULL,
    referring_dr_id         INT          NULL,
    pharmacy_id             INT          NULL,
    created_at              DATETIME2    NULL,
    archived                BIT          NULL,
    notes                   NVARCHAR(MAX) NULL,
    CONSTRAINT fk_reflog_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id),
    CONSTRAINT fk_reflog_refdr
        FOREIGN KEY (referring_dr_id) REFERENCES dbo.address_book_doctors(id),
    CONSTRAINT fk_reflog_pharmacy
        FOREIGN KEY (pharmacy_id) REFERENCES dbo.pharmacies(id)
);
GO

------------------------------------------------------------
-- 5) Appointments
------------------------------------------------------------
CREATE TABLE dbo.appointments (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    appointment_uid NVARCHAR(255)    NULL,
    patient_id      INT             NOT NULL,
    doctor_id       INT             NULL,
    start_time      DATETIME2       NULL,
    end_time        DATETIME2       NULL,
    status          NVARCHAR(50)    NULL,
    visit_type      NVARCHAR(50)    NULL,
    created_at      DATETIME2       NULL,
    created_by      INT             NULL,
    updated_at      DATETIME2       NULL,
    updated_by      INT             NULL,
    notes           NVARCHAR(MAX)   NULL,
    pharmacy_id     INT             NULL,
    CONSTRAINT fk_appt_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id),
    CONSTRAINT fk_appt_doctor
        FOREIGN KEY (doctor_id) REFERENCES dbo.address_book_doctors(id),
    CONSTRAINT fk_appt_pharmacy
        FOREIGN KEY (pharmacy_id) REFERENCES dbo.pharmacies(id)
);
GO

------------------------------------------------------------
-- 6) Patient contacts
------------------------------------------------------------
CREATE TABLE dbo.patient_contacts (
    id                      INT IDENTITY(1,1) PRIMARY KEY,
    patient_id              INT             NOT NULL,
    contact_id              INT             NULL,
    relationship            NVARCHAR(100)   NULL,
    preferred_contact_method NVARCHAR(50)   NULL,
    CONSTRAINT fk_pc_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
    -- if contact_id also points to patients, uncomment:
    -- ,CONSTRAINT fk_pc_contact
    --     FOREIGN KEY (contact_id) REFERENCES dbo.patients(id)
);
GO

------------------------------------------------------------
-- 7) document_filled_out
------------------------------------------------------------
CREATE TABLE dbo.document_filled_out (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    template_id     INT             NULL,
    patient_id      INT             NOT NULL,
    doctor_id       INT             NULL,
    date_filled     DATETIME2       NULL,
    data_json       NVARCHAR(MAX)   NULL, -- store JSON as NVARCHAR
    notes           NVARCHAR(MAX)   NULL,
    archived        BIT             NULL,
    CONSTRAINT fk_doc_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id),
    CONSTRAINT fk_doc_doctor
        FOREIGN KEY (doctor_id) REFERENCES dbo.address_book_doctors(id)
);
GO

------------------------------------------------------------
-- 8) patient_identity_verification
------------------------------------------------------------
CREATE TABLE dbo.patient_identity_verification (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    patient_id      INT             NOT NULL,
    method          NVARCHAR(50)    NULL,
    verified_at     DATETIME2       NULL,
    status          NVARCHAR(50)    NULL,
    notes           NVARCHAR(MAX)   NULL,
    CONSTRAINT fk_piv_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);
GO

------------------------------------------------------------
-- 9) patient_lesion_history
------------------------------------------------------------
CREATE TABLE dbo.patient_lesion_history (
    id                      INT IDENTITY(1,1) PRIMARY KEY,
    patient_id              INT             NOT NULL,
    image_urls              NVARCHAR(MAX)   NULL,
    body_area               NVARCHAR(100)   NULL,
    is_facing_forward       BIT             NULL,
    x_location              INT             NULL,
    y_location              INT             NULL,
    questionnaire_data      NVARCHAR(MAX)   NULL, -- JSON-ish
    review_status           NVARCHAR(50)    NULL,
    date_examined           DATETIME2       NULL,
    ai_analysis             NVARCHAR(MAX)   NULL,
    doctor_analysis         NVARCHAR(MAX)   NULL,
    admin_comments          NVARCHAR(MAX)   NULL,
    lesion_uid              NVARCHAR(255)   NULL,
    is_ai_correct           BIT             NULL,
    urgency_rating          INT             NULL,
    user_accepted_review    BIT             NULL,
    CONSTRAINT fk_plh_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);
GO

------------------------------------------------------------
-- 10) patient_notes
------------------------------------------------------------
CREATE TABLE dbo.patient_notes (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    patient_id      INT             NOT NULL,
    note            NVARCHAR(MAX)   NULL,
    created_at      DATETIME2       NULL,
    created_by      INT             NULL,
    CONSTRAINT fk_pnotes_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);
GO

------------------------------------------------------------
-- 11) promo_codes
------------------------------------------------------------
CREATE TABLE dbo.promo_codes (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    code            NVARCHAR(50)    NOT NULL UNIQUE,
    patient_id      INT             NULL,
    start_date      DATE            NULL,
    end_date        DATE            NULL,
    notes           NVARCHAR(MAX)   NULL,
    archived        BIT             NULL,
    CONSTRAINT fk_promo_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);
GO

------------------------------------------------------------
-- 12) task_notes
------------------------------------------------------------
CREATE TABLE dbo.task_notes (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    patient_id      INT             NULL,
    title           NVARCHAR(255)   NULL,
    note            NVARCHAR(MAX)   NULL,
    created_at      DATETIME2       NULL,
    created_by      INT             NULL,
    completed       BIT             NULL,
    CONSTRAINT fk_tnotes_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);
GO

------------------------------------------------------------
-- 13) uploaded_documents
------------------------------------------------------------
CREATE TABLE dbo.uploaded_documents (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    patient_id      INT             NULL,
    title           NVARCHAR(255)   NULL,
    file_name       NVARCHAR(255)   NULL,
    mime_type       NVARCHAR(100)   NULL,
    size_bytes      INT             NULL,
    uploaded_at     DATETIME2       NULL,
    uploaded_by     INT             NULL,
    archived        BIT             NULL,
    CONSTRAINT fk_udocs_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);
GO

------------------------------------------------------------
-- 14) walkin_cases
------------------------------------------------------------
CREATE TABLE dbo.walkin_cases (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    patient_id      INT             NULL,
    created_at      DATETIME2       NULL,
    status          NVARCHAR(50)    NULL,
    notes           NVARCHAR(MAX)   NULL,
    CONSTRAINT fk_walkin_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);
GO

------------------------------------------------------------
-- 15) patient_last_measurement
------------------------------------------------------------
CREATE TABLE dbo.patient_last_measurement (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    patient_id      INT             NOT NULL,
    height_cm       DECIMAL(5,2)    NULL,
    weight_kg       DECIMAL(5,2)    NULL,
    blood_pressure  NVARCHAR(20)    NULL,
    pulse           INT             NULL,
    measured_at     DATETIME2       NULL,
    measured_by     INT             NULL,
    CONSTRAINT fk_plm_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);
GO

------------------------------------------------------------
-- 16) bills
------------------------------------------------------------
CREATE TABLE dbo.bills (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    patient_id      INT             NOT NULL,
    visit_number    NVARCHAR(50)    NULL,
    invoice_number  NVARCHAR(50)    NULL,
    amount          DECIMAL(10,2)   NULL,
    issued_at       DATETIME2       NULL,
    paid_at         DATETIME2       NULL,
    status          NVARCHAR(50)    NULL,
    notes           NVARCHAR(MAX)   NULL,
    CONSTRAINT fk_bills_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);
GO

USE AICP_Database;
GO

-- if you're using dbo
CREATE TABLE dbo.patient_history (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    patient_id      INT             NOT NULL,
    change_type     NVARCHAR(100)   NULL,   -- e.g. 'update', 'create', 'archive'
    change_details  NVARCHAR(MAX)   NULL,   -- JSON/text of what changed
    changed_by      NVARCHAR(255)   NULL,   -- user or system that did it
    changed_at      DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT fk_patient_history_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);
GO

USE AICP_Database;
GO

CREATE TABLE dbo.submissions (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    patient_id      INT             NOT NULL,
    submission_type NVARCHAR(100)   NULL,   -- e.g. 'intake_form', 'questionnaire'
    submitted_at    DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME(),
    submitted_by    NVARCHAR(255)   NULL,   -- patient / staff / app
    status          NVARCHAR(50)    NULL,   -- e.g. 'pending','reviewed'
    payload         NVARCHAR(MAX)   NULL,   -- form data / JSON
    notes           NVARCHAR(MAX)   NULL,
    CONSTRAINT fk_submissions_patient
        FOREIGN KEY (patient_id) REFERENCES dbo.patients(id)
);

GO

CREATE TABLE dbo.portal_users (
  id INT IDENTITY(1,1) PRIMARY KEY,
  display_name NVARCHAR(100) NOT NULL,
  api_key NVARCHAR(128) NOT NULL UNIQUE,  -- demo: store plain; production: store hash
  role NVARCHAR(30) NOT NULL,             -- 'doctor' or 'pharmacy'
  doctor_id INT NULL,                     -- scope for doctor
  pharmacy_id INT NULL,                   -- scope for pharmacy
  is_active BIT NOT NULL DEFAULT 1,
  created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

-- Example users (replace ids with real ones)
INSERT INTO dbo.portal_users (display_name, api_key, role, doctor_id, pharmacy_id)
VALUES
('Demo Doctor',   'DOC-KEY-123', 'doctor',   8,  NULL),
('Demo Pharmacy', 'PHA-KEY-456', 'pharmacy', NULL, 3);
