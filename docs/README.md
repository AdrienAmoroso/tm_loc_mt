# Tennis Manager - Localization Translation Tool

An automated machine translation pipeline for localizing the "Tennis Manager" video game from English to any language using AI APIs.

## Overview

This tool automates the translation of in-game text from Excel-based localization files. It leverages AI (OpenAI GPT-4 or Google Gemini) to provide fast, accurate translations while preserving technical placeholders and game-specific formatting.

---

## Quick Start for End Users

### First Time Setup

#### Step 1: Create Python Virtual Environment
Open PowerShell in the project folder and run:
```powershell
python -m venv .venv
```

#### Step 2: Activate Virtual Environment and Install Dependencies

First, activate the virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` appear at the start of your PowerShell prompt.

Then, install the required packages:
```powershell
pip install -r requirements.txt
```

This will install all dependencies into your virtual environment.

#### Step 3: Set Up API Key
Create a `.env` file in the project root with your API key:
```
GEMINI_API_KEY=your_key_here
```
Or for OpenAI:
```
OPENAI_API_KEY=your_key_here
```

**Note:** Keep this file private! It contains your API credentials.

#### Step 4: Configure Translation Settings
Run the tool once - it will ask you questions:
#### Option A: Using Batch Script (Easiest)
Simply double-click:
```
scripts/run_translation.bat
```

#### Option B: Using Python
```powershell
python translate_loc.py
```

The tool will create `settings.ini` with your preferences. Answer these questions:
- **Target Language:** e.g., `Portuguese_BR`
- **Target Column Name:** e.g., `Portuguese` (must match Excel column header)
- **Sheets to Translate:** Select which sheets from the workbook
- **API Provider:** Choose Gemini (recommended) or OpenAI
- **Batch Size:** Default is 50 (higher = faster but riskier)

**Setup complete!** Your configuration is saved to `settings.ini`.

### Results

After translation completes, check:
- **Excel file:** `localization.xlsx` - Your translations are here!
- **Status report:** `logs/mt_keys_*.csv` - See which segments were translated, copied, or had issues
- **Detailed log:** `logs/mt_run_*.log` - For debugging if something went wrong

---

## Changing Configuration

### Edit Settings Anytime
Simply edit `settings.ini` in the project root:

```ini
[Translation]
target_language = Portuguese_BR
target_column = Portuguese
sheets = MATCH, STAFF
batch_size = 50

[API]
provider = gemini
max_retries = 5
```

### Reset Configuration
Delete `settings.ini` and run the tool again - it will ask setup questions.

---

## Features

- **Batch Translation:** Processes segments in configurable batches
- **Placeholder Protection:** Preserves `{[variable]}` and `<tag>` patterns
- **Dual AI Support:** Switch between Gemini and OpenAI possible
- **Smart Validation:** Ensures all tokens are preserved in correct order
- **Gap Filling:** Auto-detects and re-translates missed segments
- **DoNotTranslate Support:** Mark cells with `$donottranslate` flag to copy source unchanged
- **Rich UI:** Clean progress bars, no log clutter in console
- **Comprehensive Logging:** Detailed logs in files for debugging

---

## How It Works

1. **Load** segments from Excel localization file
2. **Filter** by translation needs:
   - Skip if source is empty
   - Skip if target already filled
   - Copy if marked `$donottranslate`
   - Translate if needs translation
3. **Protect** placeholders (e.g., `{[player]}` → `__VAR0__`)
4. **Translate** batches via AI API with retry logic and rate limit handling
5. **Validate** that all placeholders are preserved in correct order
6. **Restore** original placeholders in translation
7. **Write** results back to Excel
8. **Fill gaps** for any missed translations
9. **Report** via CSV and logs

---

## Project Structure

```
├── scripts/
│   └── run_translation.bat        # Double-click to run
├── translate_loc.py               # Main entry point
├── settings.ini                   # Configuration (created on first run)
├── .env                           # API keys (create manually)
├── localization.xlsx              # Your translation data
│
├── src/
│   ├── config.py                  # Load settings from INI
│   ├── localization_engine.py     # Main orchestrator
│   ├── translation_service.py     # AI API calls
│   ├── excel_service.py           # Excel I/O
│   ├── validation_service.py      # Translation validation
│   ├── settings_manager.py        # Settings & setup wizard
│   ├── models.py                  # Data structures
│   └── utils.py                   # Helper utilities
│
├── docs/
│   ├── README.md                  # This file
│   └── QUICK_START.md
│
├── logs/                          # Generated after each run (local only)
│   ├── mt_run_*.log               # Detailed execution logs
│   └── mt_keys_*.csv              # Per-segment status report
│
└── requirements.txt               # Python dependencies
```

---

## Technology Stack

- **Python 3.13+**
- **Excel I/O:** openpyxl, pandas
- **AI APIs:** OpenAI GPT-4o-mini, Google Gemini 2.5
- **UI:** Rich (beautiful terminal output)
- **Config:** python-dotenv, configparser

---

## Understanding the Results

### Excel Output
- **Source column:** Your original English text
- **Target column:** Translated text (filled by the tool)

### Status CSV (`logs/mt_keys_*.csv`)
Status codes:
- `OK` - Successfully translated
- `COPIED_SOURCE` - Marked `$donottranslate`, source copied
- `NO_TRANSLATION` - API returned empty
- `MISSING_TOKENS` - Translation missing placeholder tokens
- `TOKENS_OUT_OF_ORDER` - Tokens present but in wrong order

### Log File (`logs/mt_run_*.log`)
Full execution trace with:
- Configuration used
- Batch processing details
- All API interactions
- Validation results
- Any errors or warnings

---

## Troubleshooting

### "Virtual environment not found"
Run setup steps again:
```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### "API error - retrying"
This is normal! The tool automatically retries. Just wait.

### "Rate limited"
The API is busy. Tool auto-retries with backoff.

### Cells are empty or have issues
1. Check `logs/mt_keys_*.csv` for status
2. Review `logs/mt_run_*.log` for details
3. Adjust settings and re-run

### Need to change API keys
Edit `.env` file and restart the tool.

---


---

## License

Private project for Tennis Manager localization.

## Author

Adrien Amoroso  
[GitHub Profile](https://github.com/AdrienAmoroso)

---

**Status:** Production Ready  
**Last Updated:** January 22, 2026  
**Python Version:** 3.13+
