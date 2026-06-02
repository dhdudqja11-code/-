-- Migration Script: V1.2.0 - AI Regulatory Violation Details Integration
-- Purpose: Incorporate detailed legal metadata for A_LP calculation based on specific regulatory failures.

ALTER TABLE ViolationDetails 
    ADD COLUMN regulation_name VARCHAR(255) NULL, -- e.g., "GDPR Article 6" or "CCPA Right to Know"
    ADD COLUMN violation_category VARCHAR(100) NULL, -- High-level category: Data Anonymization, Consent, Bias, etc.
    ADD COLUMN failure_type_detail TEXT NULL; -- Detailed description of the failure mechanism (e.g., Linkage attack successful).

-- Indexing for performance on common search fields
CREATE INDEX idx_violation_regulation ON ViolationDetails (regulation_name);
CREATE INDEX idx_violation_category ON ViolationDetails (violation_category);