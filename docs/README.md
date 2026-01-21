# Tennis Manager - Localization Translation Tool

An automated machine translation pipeline for localizing the "Tennis Manager 25" video game from English to Portuguese (Brazilian) using AI APIs.

## Overview

This tool automates the translation of in-game text from Excel-based localization files. It leverages AI (OpenAI GPT-4 or Google Gemini) to provide fast, accurate translations while preserving technical placeholders and game-specific formatting.

**Key achievements:**
- ✅ Automated 500+ segments in minutes (vs. hours manually)
- ✅ Preserves game placeholders and technical tokens
- ✅ Intelligent batch processing with error recovery
- ✅ Comprehensive validation and logging
- ✅ Beautiful progress UI for non-technical users

## Quick Start

### For Users
```bash
# Simply run:
./scripts/run_translation.bat

# Or from Python:
python translate_loc_refactored.py
```

### For Setup (First Time Only)
```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

Create `.env` with your API key:
```
GEMINI_API_KEY=your_key_here
```

## Features

- **Batch Translation:** Processes segments in configurable batches (default: 40/batch)
- **Placeholder Protection:** Preserves `{[variable]}` and `<tag>` patterns
- **Dual AI Support:** Switch between Gemini and OpenAI with one flag
- **Smart Validation:** Ensures all tokens are preserved in correct order
- **Gap Filling:** Auto-detects and re-translates missed segments
- **Rich UI:** Progress bars and real-time status (console clutter-free)
- **Comprehensive Logging:** Detailed logs in files, important info in console

## Configuration

Edit `src/config.py`:

```python
# Sheets to translate
SHEETS_TO_TRAD = ["MP_UI", "Default", "Tuto"]

# Batch size (segments per API call)
BATCH_SIZE = 40

# Use Gemini (True) or OpenAI (False)
USE_GEMINI = True

# Target language
TARGET_LANG = "Portuguese_BR"
```

## How It Works

1. **Load** segments from Excel localization file
2. **Protect** placeholders (e.g., `{[player]}` → `__VAR0__`)
3. **Translate** batches via AI API with retry logic
4. **Validate** that all placeholders are preserved
5. **Restore** original placeholders in translation
6. **Write** results back to Excel
7. **Fill gaps** for any missed translations

## Project Structure

```
├── scripts/run_translation.bat    # Entry point for users
├── translate_loc_refactored.py    # Main entry point with UI
├── src/
│   ├── config.py                  # Configuration
│   ├── localization_engine.py     # Main orchestrator
│   ├── translation_service.py     # AI API calls
│   ├── excel_service.py           # Excel I/O
│   ├── validation_service.py      # Translation validation
│   ├── models.py                  # Data structures
│   └── utils.py                   # Helper utilities
├── docs/                          # Documentation
├── logs/                          # Generated logs (local only)
└── requirements.txt               # Dependencies
```

## Technology Stack

- **Python 3.13**
- **Excel I/O:** openpyxl, pandas
- **AI APIs:** OpenAI GPT-4o-mini, Google Gemini 2.5
- **UI:** Rich (beautiful terminal output)
- **Config:** python-dotenv

## Output

After translation completes:
- ✅ `localization.xlsx` updated with Portuguese translations
- 📊 `logs/mt_keys_*.csv` - Per-segment status report
- 📋 `logs/mt_run_*.log` - Detailed execution log

## Performance

| Dataset Size | Time | Status |
|---|---|---|
| Small (100 segments) | 1-2 min | ✅ |
| Medium (200 segments) | 2-3 min | ✅ |
| Large (500 segments) | 5-7 min | ✅ |

API rate limits handled automatically with exponential backoff.

## Error Handling

- **Rate limiting:** Automatic retry with backoff
- **Validation errors:** Logged with details, translation skipped to prevent corruption
- **Network errors:** Configurable retries (default: 5)
- **Placeholder issues:** Detailed logging for debugging

## Logging

All logs are saved locally (not uploaded to git):
- **Console:** Only warnings/errors (clean UI)
- **File:** Complete trace for debugging
- **CSV:** Per-key status for easy analysis

## Future Enhancements

- [ ] Support for additional target languages
- [ ] Web UI for non-technical users
- [ ] Automated quality scoring
- [ ] Context-aware translation hints

## License

Private project for Tennis Manager 25 localization.

## Author

Adrien Amoroso  
[GitHub Profile](https://github.com/AdrienAmoroso)

---

**Status:** Production Ready | **Last Updated:** January 21, 2026
