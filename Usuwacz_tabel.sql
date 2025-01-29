<<<<<<< HEAD
DO $$
DECLARE
    table_name TEXT;
    constraint_name TEXT;
BEGIN
    -- Usuwamy klucze obce we wszystkich tabelach w schemacie 'public'
    FOR constraint_name, table_name IN
        SELECT conname, conrelid::regclass::text
        FROM pg_constraint
        WHERE contype = 'f' AND connamespace = 'public'::regnamespace
    LOOP
        EXECUTE 'ALTER TABLE ' || quote_ident(table_name) || ' DROP CONSTRAINT ' || quote_ident(constraint_name) || ';';
    END LOOP;

    -- Usuwamy wszystkie tabele w schemacie 'public'
    FOR table_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'DROP TABLE ' || quote_ident(table_name) || ' CASCADE;';
    END LOOP;
END $$;
=======
DO $$
DECLARE
    table_name TEXT;
    constraint_name TEXT;
BEGIN
    -- Usuwamy klucze obce we wszystkich tabelach w schemacie 'public'
    FOR constraint_name, table_name IN
        SELECT conname, conrelid::regclass::text
        FROM pg_constraint
        WHERE contype = 'f' AND connamespace = 'public'::regnamespace
    LOOP
        EXECUTE 'ALTER TABLE ' || quote_ident(table_name) || ' DROP CONSTRAINT ' || quote_ident(constraint_name) || ';';
    END LOOP;

    -- Usuwamy wszystkie tabele w schemacie 'public'
    FOR table_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'DROP TABLE ' || quote_ident(table_name) || ' CASCADE;';
    END LOOP;
END $$;
>>>>>>> origin/main1
