-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set search path to include all schemas
ALTER DATABASE postgres SET search_path TO public,auth,storage,realtime;

-- Create necessary roles
CREATE ROLE anon;
CREATE ROLE authenticated;
CREATE ROLE service_role;

-- Create roles
CREATE ROLE anon;
ALTER ROLE anon WITH NOLOGIN;

CREATE ROLE authenticated;
ALTER ROLE authenticated WITH NOLOGIN;

CREATE ROLE service_role;
ALTER ROLE service_role WITH NOLOGIN;

-- Set JWT secret for anon role
ALTER ROLE anon SET "jwt.secret" = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFxb2tjanNtYWpucGZrbGFkdWJwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzOTg4OTUsImV4cCI6MjA2Njk3NDg5NX0.f2Z4aRkTlUExrpir4fqIpn0TkzpS5B0WPuAHAb26YFM';

-- Set search_path for all roles
ALTER ROLE anon SET search_path TO public,auth,storage,realtime;
ALTER ROLE authenticated SET search_path TO public,auth,storage,realtime;
ALTER ROLE service_role SET search_path TO public,auth,storage,realtime;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS storage;
CREATE SCHEMA IF NOT EXISTS realtime;

-- Create test table in public schema
CREATE TABLE IF NOT EXISTS public.test_table (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert test data
INSERT INTO public.test_table (name) VALUES ('Test Row 1');

-- Grant permissions
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

-- Insert test user
INSERT INTO auth.users (email, encrypted_password, raw_app_meta_data, raw_user_meta_data, is_super_admin)
VALUES (
    'test@example.com',
    crypt('password123', gen_salt('bf')),
    '{"provider": "email"}'::jsonb,
    '{"full_name": "Test User"}'::jsonb,
    false
) ON CONFLICT (email) DO NOTHING;

-- Create auth tables
CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    email VARCHAR(255) UNIQUE,
    encrypted_password VARCHAR(255),
    confirmed_at TIMESTAMP WITH TIME ZONE,
    confirmation_token VARCHAR(255) UNIQUE,
    confirmation_sent_at TIMESTAMP WITH TIME ZONE,
    recovery_token VARCHAR(255) UNIQUE,
    recovery_sent_at TIMESTAMP WITH TIME ZONE,
    email_change_token_new VARCHAR(255) UNIQUE,
    email_change VARCHAR(255),
    email_change_sent_at TIMESTAMP WITH TIME ZONE,
    last_sign_in_at TIMESTAMP WITH TIME ZONE,
    raw_app_meta_data JSONB,
    raw_user_meta_data JSONB,
    is_super_admin BOOLEAN DEFAULT false,
    disabled_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create test table in public schema
CREATE TABLE IF NOT EXISTS public.test_table (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert test data
INSERT INTO public.test_table (name) VALUES ('Test Row 1');

-- Grant permissions
GRANT SELECT ON public.test_table TO anon;
GRANT SELECT ON public.test_table TO authenticated;
GRANT SELECT ON public.test_table TO service_role;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON auth.users(email);
CREATE INDEX IF NOT EXISTS idx_users_confirmed_at ON auth.users(confirmed_at);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON auth.users(created_at);

-- Create public users view
CREATE OR REPLACE VIEW public.users AS
SELECT id, email, raw_app_meta_data, raw_user_meta_data, is_super_admin
FROM auth.users
WHERE deleted_at IS NULL
WITH CHECK OPTION;

-- Grant permissions on the public users view
GRANT SELECT ON public.users TO anon;
GRANT SELECT ON public.users TO authenticated;
GRANT SELECT ON public.users TO service_role;

-- Create test user
INSERT INTO auth.users (email, encrypted_password, confirmed_at, raw_app_meta_data)
VALUES (
    'test@example.com',
    crypt('password123', gen_salt('bf')),
    NOW(),
    '{"provider": "email", "providers": ["email"]}'::jsonb
);

-- Create storage tables
CREATE TABLE IF NOT EXISTS storage.buckets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    owner UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    public BOOLEAN DEFAULT false,
    file_size_limit BIGINT DEFAULT 52428800, -- 50MB
    allowed_mime_types TEXT[] DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS storage.objects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bucket_id UUID REFERENCES storage.buckets(id),
    name TEXT NOT NULL,
    owner UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    path_tokens TEXT[] DEFAULT '{}',
    mime_type TEXT,
    size BIGINT,
    CONSTRAINT objects_name_bucket_id_key UNIQUE (name, bucket_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_objects_bucket_id ON storage.objects(bucket_id);
CREATE INDEX IF NOT EXISTS idx_objects_owner ON storage.objects(owner);
CREATE INDEX IF NOT EXISTS idx_objects_path_tokens ON storage.objects USING GIN (path_tokens);
CREATE INDEX IF NOT EXISTS idx_objects_search ON storage.objects USING GIN (to_tsvector('english', name));

-- Grant table permissions
GRANT USAGE ON SCHEMA storage TO authenticated;
GRANT USAGE ON SCHEMA storage TO service_role;

GRANT USAGE ON SCHEMA realtime TO anon;
GRANT USAGE ON SCHEMA realtime TO authenticated;
GRANT USAGE ON SCHEMA realtime TO service_role;

-- Grant permissions on tables
GRANT SELECT ON TABLE auth.users TO anon;
GRANT SELECT ON TABLE auth.users TO authenticated;
GRANT SELECT ON TABLE auth.users TO service_role;

GRANT SELECT ON TABLE storage.buckets TO anon;
GRANT SELECT ON TABLE storage.objects TO anon;
GRANT SELECT ON TABLE storage.objects TO authenticated;
GRANT SELECT ON TABLE storage.objects TO service_role;
GRANT INSERT ON TABLE storage.objects TO authenticated;
GRANT UPDATE ON TABLE storage.objects TO authenticated;
GRANT DELETE ON TABLE storage.objects TO authenticated;

GRANT SELECT ON ALL TABLES IN SCHEMA realtime TO anon;
GRANT SELECT ON ALL TABLES IN SCHEMA realtime TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA realtime TO service_role;

CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Grant permissions on tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA auth TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA auth TO anon;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA auth TO authenticated;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA auth TO service_role;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA storage TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA storage TO anon;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA storage TO authenticated;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA storage TO service_role;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO service_role;
