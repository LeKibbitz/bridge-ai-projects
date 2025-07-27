# FFB Database Project

This project aims to scrape data from the French Bridge Federation (FFB) website to build a comprehensive and structured database using Python, Selenium, and Supabase.

## 🚀 Core Functionality

The project is composed of two main Python scripts:

1.  **`scripts/scraper.py`**: A robust, interactive web scraper that logs into the FFB "espace métier", navigates to different entity pages (FFB, Zone, Ligue, Comité, Club), and extracts detailed information. It features an interactive menu to select specific entities or run batch scraping operations.

2.  **`scripts/create_database_schema.py`**: A schema generator that analyzes the structure of the scraped data and produces a complete database schema in both `JSON` and `SQL` formats. This script is currently being refactored to align with a new, unified entity model.

## 🔧 Project Status & Next Steps

The project is under active development. Here is the current status:

-   **Scraper (`scraper.py`)**:
    -   Successfully logs in and navigates to the "espace métier".
    -   Provides an interactive menu to choose which entity type to scrape.
    -   The core scraping logic is being refactored to handle different entity types and their specific data layouts.
    -   A bug related to scraping "Zone" entities has been fixed.

-   **Schema Generator (`create_database_schema.py`)**:
    -   The script is being overhauled to generate a more unified and coherent database schema based on user feedback.
    -   **Upcoming Changes**:
        -   Consolidate all direct entity attributes into a single `entities` table.
        -   Use explicit, English, snake_case names for all tables and fields, derived from UI labels.
        -   Create separate tables for related lists (e.g., `actors`, `roles`) linked by a foreign key.
        -   Ensure standard metadata fields (`created_at`, `created_by`, etc.) are correctly ordered at the end of each table.

## ⚙️ How to Run

### 1. Setup Environment

-   Ensure you have Python 3 installed.
-   Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
-   Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
-   Make sure you have a `scripts/config.py` file with your `FFB_USERNAME` and `FFB_PASSWORD`.

### 2. Run the Scraper

To run the interactive scraper:

```bash
python3 scripts/scraper.py
```

You will be presented with a menu to choose which entity to scrape.

## 🗂️ Project Structure

```
FFB_Database/
├── scripts/
│   ├── scraper.py               # The main interactive scraper
│   ├── create_database_schema.py  # The database schema generator
│   ├── config.py                # Configuration file (credentials)
│   └── ...
├── FFB_Scraped_Data/
│   ├── database_schema.json     # Generated JSON schema
│   └── database_schema.sql      # Generated SQL schema
├── docs/
│   └── DB_Schema_Builder_by_Web_Navigation.txt # Detailed scraping instructions
└── README.md                    # This file
```

## 📝 Development Notes

-   The scraper is designed to be resilient, with explicit waits and error handling for navigation and data extraction.
-   The schema generation process is evolving to produce a cleaner, more normalized database structure.
-   Regular commits are made to ensure progress is saved and the project history is clean.

## 📚 Legacy Information

The project previously contained more complex setup instructions related to Node.js and Prisma, which are no longer the primary focus. The current approach is centered around the Python scraping and schema generation scripts. The `docs` folder contains historical and specification files that guide the development of the scraper.
