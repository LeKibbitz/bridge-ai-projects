# FFB Database Project Overview

## Goal

The FFB Database project automates the extraction, transformation, and loading (ETL) of club and player data from the Fédération Française de Bridge (FFB) website into a modern, queryable Supabase/PostgreSQL database. This enables advanced analytics, reporting, and integration with other systems.

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
- **Note:** Selenium/ChromeDriver setup on Mac ARM can be tricky. If you get an error about `THIRD_PARTY_NOTICES.chromedriver`, ensure your script finds the real `chromedriver` binary, not a documentation file. See the `_setup_driver` method for robust handling.

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

## Workflow Options

### Option A: Local Scraping + Codespaces Import (Recommended)
This approach avoids browser/driver issues in Codespaces by separating scraping and importing:

1. **Scrape locally** (where you have full control over Chrome/ChromeDriver):
   ```sh
   python legacy/FFB_Data/scraper.py
   ```

2. **Commit and push CSVs** to GitHub:
   ```sh
   git add clubs.csv players.csv
   git commit -m "Update clubs and players data"
   git push
   ```

3. **Import from Codespaces** (where Supabase connection is configured):
   ```sh
   node scripts/import-data.js
   ```

**Benefits:**
- Avoids ChromeDriver issues in Codespaces
- Keeps scraping and importing decoupled
- Works reliably on local machines with Chrome installed

### Option B: Full Codespaces Workflow
Use Codespaces for both scraping and importing (requires Playwright instead of Selenium).

---

## ChromeDriver Troubleshooting for Mac ARM

If you encounter issues with ChromeDriver (e.g., "killed", "cannot connect to service", or permission errors), follow these steps:

1. **Check your installed Chrome version:**
   ```sh
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version
   ```
2. **Download the matching ChromeDriver (mac-arm64) from:**
   [Chrome for Testing Downloads](https://googlechromelabs.github.io/chrome-for-testing/)
3. **Unzip and move the binary:**
   ```sh
   mv /path/to/chromedriver-mac-arm64/chromedriver ~/chromedriver_arm64
   chmod +x ~/chromedriver_arm64
   ```
4. **Test the binary:**
   ```sh
   ~/chromedriver_arm64 --version
   ```
   You should see output like `ChromeDriver 138.0.7204.101 ...`.
5. **Update your script to use this path:**
   ```python
   driver_path = "/Users/lekibbitz/chromedriver_arm64"
   service = Service(driver_path)
   driver = webdriver.Chrome(service=service, options=options)
   ```
6. **Run your script as usual.**

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
   - _If you get a ChromeDriver error, check the driver path logic in `_setup_driver`._
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
- Troubleshoot and document Selenium/ChromeDriver issues for Mac ARM
- Update requirements.txt and scraper.py for local Selenium workflow

---

## Contact & Next Steps

- For any questions, check this file and the README.
- Continue with the workflow above, commit and push after each step.
- If you add new features or fix bugs, document them here for the next teammate! 