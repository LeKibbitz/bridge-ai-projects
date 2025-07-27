#!/bin/bash
# Migration script for Bridge-Arbitrage

# Check if we're in the correct directory
cd $(dirname "$0")/..

# Create migrations directory if it doesn't exist
mkdir -p migrations

# Get current date for migration file
date=$(date +%Y%m%d_%H%M%S)

# Create new migration file
touch migrations/${date}_migration.sql

# Make the script executable
chmod +x $0

echo "Created new migration file: migrations/${date}_migration.sql"
echo "Edit this file with your migration SQL statements"
