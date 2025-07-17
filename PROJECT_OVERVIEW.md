# FFB Database Project Overview

## Goal

The FFB Database project aims to automate the extraction, transformation, and loading (ETL) of club and player data from the Fédération Française de Bridge (FFB) website into a modern, queryable Supabase/PostgreSQL database. This enables advanced analytics, reporting, and integration with other systems.

---

## Technical Stack

- **Backend Database:** Supabase (PostgreSQL, managed)
- **ORM:** Prisma (TypeScript/Node.js)
- **Data Import:**
  - **Web Scraping:** Python (Selenium, pandas, BeautifulSoup)
  - **CSV Parsing & DB Import:** Node.js (csv-parser, Prisma Client)
- **Automation/DevOps:** GitHub Codespaces (for cloud-based workflow), Git for version control
- **Other:** dotenv for config, requirements.txt for Python deps, package.json for Node.js deps

---

## Architecture

```mermaid
graph TD
  A[FFB Website] -- Selenium Scraper --> B[CSV Files (clubs.csv, players.csv)]
  B -- import-data.js --> C[Supabase DB]
  C -- Prisma Client --> D[Node.js/JS Apps]
  C -- Supabase Dashboard --> E[Manual Admin/Queries]
```

- **Scraper:** Python script logs in, navigates, and extracts data from FFB, outputs CSVs.
- **Importer:** Node.js script reads CSVs and upserts data into Supabase via Prisma.
- **Database:** Prisma schema defines tables for clubs, players, roles, functions, and join tables.

---

## Dataflows & Processes

### 1. Scraping
- Run `scraper.py` (in `legacy/FFB_Data/`) to extract club and player data from the FFB website.
- Outputs: `clubs.csv`, `players.csv` (in project root)

### 2. Review/QA
- Open and check the CSVs for completeness and correctness.

### 3. Import
- Run `node scripts/import-data.js` to import CSV data into Supabase DB using Prisma.
- Data is upserted (inserted or updated) to avoid duplicates.

### 4. Verification
- Use Supabase dashboard or `scripts/test-connection.js` to verify data.

### 5. (Optional) Add Indexes & Triggers
- Run SQL scripts in Supabase SQL editor for performance and data integrity.

---

## Commit & Push Workflow

- **After every major step (scraper update, CSV generation, import, schema change, etc.), run:**
  ```sh
  git add .
  git commit -m "<describe change>"
  git push
  ```
- This ensures all progress is saved and teammates can pick up from the latest state.

---

## Directory Structure (Key Parts)

```
FFB_Database/
├── clubs.csv                # Output from scraper, input to importer
├── players.csv              # Output from scraper, input to importer
├── prisma/
│   └── schema.prisma        # Prisma DB schema
├── scripts/
│   ├── import-data.js       # Node.js CSV importer
│   └── test-connection.js   # DB connection tester
├── legacy/FFB_Data/
│   ├── scraper.py           # Selenium web scraper
│   ├── models.py            # Data models for scraping
│   ├── config.py            # Scraper config (credentials, URLs)
│   └── requirements.txt     # Python dependencies
├── PROJECT_OVERVIEW.md      # This documentation
└── ...
```

---

## How to Take Over

1. **Clone the repo and set up Codespaces or your local dev environment.**
2. **Check `.env` for correct Supabase connection string.**
3. **Install Python and Node.js dependencies:**
   - `pip install -r legacy/FFB_Data/requirements.txt`
   - `npm install`
4. **Run the scraper:**
   - `python legacy/FFB_Data/scraper.py`
5. **Review CSVs:**
   - `head -20 clubs.csv`
   - `head -20 players.csv`
6. **Import data:**
   - `node scripts/import-data.js`
7. **Verify in Supabase dashboard.**
8. **Commit and push after each major step.**

---

## Recent Key Commits

- Set up Supabase DB, Prisma schema, indexes, triggers, and added Scrapping.py for website data extraction
- Add legacy/FFB_Data with latest scraping and utility scripts for review and integration
- Add CSV export to scraper.py for clubs and players matching current DB schema
- Test full workflow: update Scrapping.py, import-data.js, and CSVs for Codespaces run

---

## Contact & Next Steps

- For any questions, check this file and the README.
- Continue with the workflow above, commit and push after each step.
- If you add new features or fix bugs, document them here for the next teammate! 