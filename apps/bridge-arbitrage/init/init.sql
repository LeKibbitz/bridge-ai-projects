-- Set up roles
CREATE ROLE anon;
ALTER ROLE anon WITH NOLOGIN;
ALTER ROLE anon SET search_path TO public,auth,storage,realtime;

CREATE ROLE authenticated;
ALTER ROLE authenticated WITH NOLOGIN;
ALTER ROLE authenticated SET search_path TO public,auth,storage,realtime;

CREATE ROLE service_role;
ALTER ROLE service_role WITH NOLOGIN;
ALTER ROLE service_role SET search_path TO public,auth,storage,realtime;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS storage;
CREATE SCHEMA IF NOT EXISTS realtime;

-- Create configuration table
CREATE TABLE IF NOT EXISTS auth.jwt_secrets (
    role_name TEXT PRIMARY KEY,
    secret TEXT NOT NULL
);

-- Insert JWT secret
-- Remove JWT secret from role configuration
ALTER ROLE anon SET "jwt.secret" = '';

-- Install required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create test table in public schema
CREATE TABLE IF NOT EXISTS public.test_table (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert test data if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.test_table) THEN
        INSERT INTO public.test_table (name) VALUES ('Test Row 1');
    END IF;
END $$;

-- Grant permissions
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT ON public.test_table TO anon;
GRANT SELECT ON public.test_table TO authenticated;
GRANT SELECT ON public.test_table TO service_role;

-- Create auth.users table
CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    encrypted_password VARCHAR(255) NOT NULL,
    raw_app_meta_data JSONB NOT NULL DEFAULT '{}',
    raw_user_meta_data JSONB NOT NULL DEFAULT '{}',
    is_super_admin BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON auth.users(email);
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON auth.users(deleted_at);

-- Create public.users view
CREATE OR REPLACE VIEW public.users AS
SELECT id, email, raw_app_meta_data, raw_user_meta_data, is_super_admin
FROM auth.users
WHERE deleted_at IS NULL
WITH CHECK OPTION;

-- Grant permissions on auth schema
GRANT USAGE ON SCHEMA auth TO anon;
GRANT SELECT ON auth.users TO anon;
GRANT SELECT ON auth.users TO authenticated;
GRANT SELECT ON auth.users TO service_role;

-- Grant permissions on public.users view
GRANT SELECT ON public.users TO anon;
GRANT SELECT ON public.users TO authenticated;
GRANT SELECT ON public.users TO service_role;
