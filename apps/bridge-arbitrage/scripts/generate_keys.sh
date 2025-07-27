#!/bin/bash

# Générer une clé sécurisée de 32 caractères
function generate_key() {
    openssl rand -base64 32 | tr -d "\n"
}

echo "POSTGRES_PASSWORD=$(generate_key)"
echo "SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJyaWRnZmFjaWxlIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODk0MjM4MjcsImV4cCI6MjAwNTAwMjgyN30.1234567890"
echo "SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJyaWRnZmFjaWxlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY4OTQyMzgyNywibmJmIjoxNjg5NDIzODI3LCJleHAiOjIwMDUwMDI4Mjd9.1234567890"
echo "DEPLOYMENT_ENVIRONMENT=production"
