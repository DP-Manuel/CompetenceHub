\set ON_ERROR_STOP on

BEGIN;
SET LOCAL ROLE competence_hub_owner;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'competence_hub'
          AND table_name = 'coaches'
          AND column_name = 'public_profile_path'
          AND is_nullable = 'YES'
    ) THEN
        RAISE EXCEPTION 'public_profile_path is missing or not nullable';
    END IF;
END
$$;

INSERT INTO competence_hub.coaches (
    display_name, public_profile_status, public_profile_path
) VALUES (
    'Synthetic Profile One', 'synthetic', '/coaches/synthetic-one/'
), (
    'Synthetic Profile Null One', 'synthetic', NULL
), (
    'Synthetic Profile Null Two', 'synthetic', NULL
);

DO $$
DECLARE
    unsafe_path text;
BEGIN
    BEGIN
        INSERT INTO competence_hub.coaches (
            display_name, public_profile_status, public_profile_path
        ) VALUES (
            'Synthetic Duplicate', 'synthetic', '/coaches/synthetic-one/'
        );
        RAISE EXCEPTION 'Duplicate public profile path was accepted';
    EXCEPTION
        WHEN unique_violation THEN NULL;
    END;

    FOREACH unsafe_path IN ARRAY ARRAY[
        'https://example.invalid/coaches/test/',
        '//example.invalid/coaches/test/',
        '/coaches/test/?x=1',
        '/coaches/test/#fragment',
        '/coaches/../admin/',
        '/kontakt/',
        '/coaches/Test/',
        '/coaches/test',
        '/coaches/test%2fadmin/',
        '/coaches/' || repeat('a', 192) || '/'
    ]
    LOOP
        BEGIN
            INSERT INTO competence_hub.coaches (
                display_name, public_profile_status, public_profile_path
            ) VALUES (
                'Synthetic Unsafe Path', 'synthetic', unsafe_path
            );
            RAISE EXCEPTION 'Unsafe public profile path was accepted: %', unsafe_path;
        EXCEPTION
            WHEN check_violation THEN NULL;
        END;
    END LOOP;

    IF (
        SELECT count(*)
        FROM competence_hub.coaches
        WHERE display_name LIKE 'Synthetic Profile %'
          AND public_profile_path IS NULL
    ) <> 2 THEN
        RAISE EXCEPTION 'Multiple NULL profile paths were not retained';
    END IF;
END
$$;

ROLLBACK;
