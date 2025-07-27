#!/bin/bash

# Check if supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "Error: Supabase CLI is not installed. Please install it first."
    exit 1
fi

# Get project ID from supabase config
PROJECT_ID=$(supabase project id)

if [ -z "$PROJECT_ID" ]; then
    echo "Error: Could not get Supabase project ID. Please make sure you're logged in to Supabase CLI."
    exit 1
fi

echo "Updating tables with new fields..."

echo "1. Creating backup of existing tables..."
supabase sql -f scripts/backup_existing_tables.sql

if [ $? -ne 0 ]; then
    echo "Error creating backup tables"
    exit 1
fi

echo "2. Running migration to add new fields..."
supabase sql -f scripts/migrate_to_nullable.sql

if [ $? -ne 0 ]; then
    echo "Error running migration"
    exit 1
fi

echo "3. Verifying new table structure..."

# Verify the new structure using psql
supabase sql -c "\d rnc_articles" -c "\d code_laws"

echo "Tables updated successfully!"
