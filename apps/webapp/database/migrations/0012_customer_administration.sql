\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

CREATE TABLE competence_hub.private_customers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name text NOT NULL CHECK (char_length(btrim(first_name)) BETWEEN 1 AND 100),
    last_name text NOT NULL CHECK (char_length(btrim(last_name)) BETWEEN 1 AND 100),
    email text CHECK (char_length(email) BETWEEN 3 AND 254 AND position('@' IN email) > 1),
    phone text CHECK (char_length(btrim(phone)) BETWEEN 1 AND 50),
    address_street text CHECK (char_length(btrim(address_street)) BETWEEN 1 AND 200),
    address_postal_code text CHECK (char_length(btrim(address_postal_code)) BETWEEN 1 AND 20),
    address_city text CHECK (char_length(btrim(address_city)) BETWEEN 1 AND 120),
    address_country text CHECK (char_length(btrim(address_country)) BETWEEN 1 AND 100),
    version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK (num_nonnulls(address_street, address_postal_code, address_city, address_country) IN (0, 4))
);

CREATE TABLE competence_hub.company_customer_details (
    company_id uuid PRIMARY KEY REFERENCES competence_hub.companies(id) ON DELETE RESTRICT,
    vat_id text CHECK (vat_id ~ '^[A-Z0-9]{3,32}$'),
    address_purpose text CHECK (address_purpose IN ('business', 'billing')),
    address_street text CHECK (char_length(btrim(address_street)) BETWEEN 1 AND 200),
    address_postal_code text CHECK (char_length(btrim(address_postal_code)) BETWEEN 1 AND 20),
    address_city text CHECK (char_length(btrim(address_city)) BETWEEN 1 AND 120),
    address_country text CHECK (char_length(btrim(address_country)) BETWEEN 1 AND 100),
    version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK (num_nonnulls(address_purpose, address_street, address_postal_code,
                        address_city, address_country) IN (0, 5))
);

REVOKE ALL ON competence_hub.private_customers, competence_hub.company_customer_details
    FROM PUBLIC, competence_hub_app;
GRANT SELECT, INSERT ON competence_hub.private_customers, competence_hub.company_customer_details
    TO competence_hub_app;
GRANT UPDATE (first_name, last_name, email, phone, address_street, address_postal_code,
              address_city, address_country, version, updated_at)
    ON competence_hub.private_customers TO competence_hub_app;
GRANT UPDATE (vat_id, address_purpose, address_street, address_postal_code, address_city,
              address_country, version, updated_at)
    ON competence_hub.company_customer_details TO competence_hub_app;

INSERT INTO competence_hub.schema_migrations (version, description)
VALUES ('0012', 'Internal private customers and optional company customer details');
COMMIT;
