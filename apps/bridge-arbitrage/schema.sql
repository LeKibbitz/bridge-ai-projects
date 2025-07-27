-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables with their relationships

-- bidding_categories table
CREATE TABLE IF NOT EXISTS public.bidding_categories (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- code_laws table
CREATE TABLE IF NOT EXISTS public.code_laws (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- conventions_documents table
CREATE TABLE IF NOT EXISTS public.conventions_documents (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- document_versions table
CREATE TABLE IF NOT EXISTS public.document_versions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    document_id UUID NOT NULL,
    version_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (document_id) REFERENCES conventions_documents(id)
);

-- law_references table
CREATE TABLE IF NOT EXISTS public.law_references (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    law_id UUID NOT NULL,
    article_number TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (law_id) REFERENCES code_laws(id)
);

-- rnc_articles table
CREATE TABLE IF NOT EXISTS public.rnc_articles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- rpi_articles table
CREATE TABLE IF NOT EXISTS public.rpi_articles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add RLS policies
ALTER TABLE public.bidding_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.code_laws ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conventions_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.law_references ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rnc_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rpi_articles ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY "Enable read access for authenticated users" ON public.bidding_categories
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON public.code_laws
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON public.conventions_documents
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON public.document_versions
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON public.law_references
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON public.rnc_articles
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for authenticated users" ON public.rpi_articles
    FOR SELECT
    USING (auth.role() = 'authenticated');
