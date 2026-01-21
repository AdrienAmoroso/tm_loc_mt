# Tennis Manager - Localization Translation Tool

## Quick Start (1 Minute)

### How to Run
1. **Double-click:** `run_translation.bat`
2. **Watch:** Progress bars show translation progress
3. **Done:** Check `localization.xlsx` for Portuguese_BR translations

That's it! Your tool now automatically translates game text using AI.

---

## For Non-Technical Users (5 Minutes)

### What Does This Tool Do?
- Reads English text from Excel
- Translates to Portuguese (using AI)
- Writes translations back to Excel
- Fills any missed translations

### How to Use It
1. **Open folder:** `C:\Users\AdrienAmoroso\Rebound\tm_loc_mt`
2. **Double-click:** `run_translation.bat`
3. **Watch the progress bars** as translations happen
4. **Press Enter** when you see "Translation completed"
5. **Open Excel:** Check the Portuguese_BR column - it's filled with translations!

### What You'll See
```
Tennis Manager - Localization Translation

Configuration
Target Language: Portuguese_BR
Sheets: MP_UI
Batch Size: 40

Starting translation phase
MP_UI ------ ------- --------   5/10 [00:30<01:15]

Translation completed successfully!
```

### Time Needed
- Small sheet (100 segments): 1-2 minutes
- Medium sheet (200 segments): 2-3 minutes
- Large sheet (500 segments): 5-7 minutes

### If Something Goes Wrong

**"Virtual environment not found"**
- Ask your IT person to set it up (one-time only)

**"API error - retrying"**
- This is normal! The tool automatically retries
- Just wait, it will succeed

**Translation quality seems wrong**
- Check the log file: `logs/mt_run_*.log`
- Look at status file: `logs/mt_keys_*.csv`

**Still stuck?**
- Share the error message from the log file with your developer

---

## For Developers (10 Minutes)

### Configuration

Edit `config.py` to customize:

```python
# Sheets to translate
SHEETS_TO_TRAD = [
    "MP_UI",
    # "Default",
    # "Tuto",
]

# Batch size (segments per API call)
# 20 = safe, 40 = recommended, 50 = fast
BATCH_SIZE = 40

# Target language
TARGET_LANG = "Portuguese_BR"
TARGET_COL = "Portuguese_BR"

# Use Gemini (True) or OpenAI (False)
USE_GEMINI = True
```

### Architecture

The tool consists of modular services:

- **`config.py`** - Configuration management
- **`excel_service.py`** - Read/write Excel files
- **`translation_service.py`** - AI translation (Gemini + OpenAI)
- **`validation_service.py`** - Check placeholder preservation
- **`localization_engine.py`** - Main orchestration with progress bars
- **`utils.py`** - Placeholder protection utilities
- **`models.py`** - Data structures
- **`translate_loc_refactored.py`** - Entry point with UI

### How Translation Works

1. **Load segments** from Excel sheet
2. **Protect placeholders** (`{[player]}` → `__VAR0__`)
3. **Send batches to AI** (Gemini or OpenAI)
4. **Validate translations** (check placeholders preserved)
5. **Restore placeholders** (`__VAR0__` → `{[player]}`)
6. **Write to Excel** and log results
7. **Fill gaps** (re-translate any blanks)

### Placeholder System

The tool preserves game-specific placeholders:

```
{[player_name]}  → __VAR0__  → Olá {[player_name]}
<strong>text</strong> → __TAG0__ → <strong>texto</strong>
```

This ensures translations don't break game functionality.

### API Keys

Create `.env` file with:
```
GEMINI_API_KEY=your_key_here
```

Or for OpenAI:
```
OPENAI_API_KEY=your_key_here
```

### Batch Size Guidance

- **Batch Size 20:** Safe, good error isolation, but slower
- **Batch Size 40:** Recommended (best balance)
- **Batch Size 50:** Fast, still safe
- **Batch Size 100+:** Risk timeout, not recommended

### Running Directly (Python)

```bash
# Using refactored version with UI
python translate_loc_refactored.py

# Or old monolithic version (still works)
python translate_loc.py
```

### Understanding Log Files

**File:** `logs/mt_run_YYYYMMDD_HHMMSS.log`
- Detailed execution trace
- All API calls and responses
- Error messages and warnings
- For debugging

**File:** `logs/mt_keys_YYYYMMDD_HHMMSS.csv`
- Per-key translation status
- Columns: sheet, key, row, language, status
- Status codes: `OK`, `MISSING_TOKENS`, `TOKENS_OUT_OF_ORDER`, `NO_TRANSLATION`

---

## Troubleshooting

### Progress Bar Doesn't Move
- This is normal! Batch is being translated
- Check log file to see API responses

### 503 Service Unavailable / Rate Limited
- API is overloaded
- Code automatically retries with exponential backoff
- Just wait, it will succeed

### Placeholders Missing in Translation
- Check `logs/mt_keys_*.csv` for status
- Look for `MISSING_TOKENS` entries
- Re-run translation for those segments

### "Sheet not found"
- Check `config.py` SHEETS_TO_TRAD list
- Sheet names are case-sensitive
- Make sure names match Excel exactly

### Excel File Locked
- Close `localization.xlsx` in Excel
- Tool can't write to open files

### API Key Error
- Check `.env` file exists
- Verify key is correct: `GEMINI_API_KEY` or `OPENAI_API_KEY`
- Check key has proper permissions

---

## File Structure

```
Project Root
├── run_translation.bat ................. Double-click to run
├── config.py .......................... Settings & constants
├── localization.xlsx .................. Your translation data
├── .env .............................. API keys
│
├── Core Modules (all modular & testable)
├── translate_loc_refactored.py ........ Entry point with UI
├── localization_engine.py ............. Orchestration
├── translation_service.py ............. API calls
├── excel_service.py ................... Excel I/O
├── validation_service.py .............. Validation
├── models.py .......................... Data structures
└── utils.py ........................... Utilities

├── Logs (created after each run)
├── logs/mt_run_YYYYMMDD_HHMMSS.log .. Execution log
└── logs/mt_keys_YYYYMMDD_HHMMSS.csv . Per-key status
```

---

## Performance Tips

### Faster Translation
- Increase `BATCH_SIZE` to 40-50
- Use Gemini (faster than OpenAI)
- Reduce number of sheets per run

### Lower API Costs
- Use OpenAI gpt-4o-mini (cheaper than GPT-4)
- Adjust batch size carefully
- Monitor logs for failed batches

### Better Results
- Review log files for errors
- Check gap-filling report
- Spot-check quality in Excel

---

## Advanced Configuration

### Switch API Providers

```python
# In config.py
USE_GEMINI = True   # Fast & free tier available
USE_GEMINI = False  # Use OpenAI instead
```

### Adjust Rate Limiting

```python
# Time to wait between batches (prevent throttling)
BATCH_COOLDOWN_SECONDS = 22.0

# Max retries for failed API calls
max_retries_gemini = 5
max_retries_openai = 5
```

### Custom Sheets

```python
SHEETS_TO_TRAD = [
    "MP_UI",
    "Default",
    "Tuto",
    "Match",
]
```

---

## Common Workflows

### Translate One Sheet
1. Edit `config.py`: `SHEETS_TO_TRAD = ["MP_UI"]`
2. Double-click `run_translation.bat`
3. Check results in Excel

### Translate Multiple Sheets
1. Edit `config.py` with all sheet names
2. Double-click `run_translation.bat`
3. Wait for completion
4. Review `logs/mt_keys_*.csv` for any issues

### Check Translation Quality
1. Open `logs/mt_keys_*.csv` in Excel
2. Filter for status != "OK"
3. Check those specific translations
4. Re-run if needed

### Migrate Old to New Version
1. Old script still works: `python translate_loc.py`
2. New script has UI: `python translate_loc_refactored.py`
3. Both produce same results
4. Gradually migrate to new version

---

## FAQ

**Q: Is the AI translation good quality?**  
A: Very good for game localization. Review sample translations, adjust if needed.

**Q: Can I use offline?**  
A: No, requires active internet for API calls.

**Q: How much does it cost?**  
A: Depends on API provider (Gemini free tier / OpenAI paid). Check their pricing.

**Q: Can I translate to other languages?**  
A: Yes! Edit `config.py`: `TARGET_LANG = "Spanish"` and adjust column name.

**Q: What if translations are wrong?**  
A: Edit Excel manually or adjust batch and re-run specific sheet.

**Q: Can I run multiple translations at once?**  
A: One at a time recommended. API rate limits may cause issues.

**Q: How do I backup my translations?**  
A: Keep `.xlsx` backups before running. Tool preserves existing translations.

**Q: Can non-technical people use this?**  
A: Yes! Just double-click `run_translation.bat` and wait.

---

## Support & Troubleshooting

### Getting Help
1. Check the log file: `logs/mt_run_*.log`
2. Look at status file: `logs/mt_keys_*.csv`
3. Review this README's Troubleshooting section
4. Ask your developer with the log file attached

### Reporting Issues
Include:
- Error message from console
- Log file content (`logs/mt_run_*.log`)
- Configuration used (`config.py`)
- Which sheets were being translated

### Testing New Features
1. Create a backup: `cp localization.xlsx localization.xlsx.backup`
2. Test with one small sheet first
3. Check quality of results
4. Gradually add more sheets

---

## Version History

- **Current:** Refactored modular version with Rich UI
- **Previous:** Original monolithic script (still available)

Both versions work identically. New version has:
- Better code organization
- Beautiful progress UI
- Easier to maintain
- Easier to extend

---

**Status:** Production-ready  
**Last Updated:** January 20, 2026  
**Reliability:** ⭐⭐⭐⭐⭐  
**Team Ready:** YES  

For quick reference, see `QUICK_START.md`

---

## Git & Version Control

### Initial Setup (Already Done!)
```bash
# Repository initialized
git init
git config user.email "adrien.amoroso@etu.univ-tours.fr"
git config user.name "AdrienAmoroso"
```

### Making Changes
```bash
# See what changed
git status

# Stage changes
git add .

# Commit with message
git commit -m "Feature: describe what you changed"

# View history
git log --oneline
```

### Pushing to Remote
```bash
# Add remote (one time)
git remote add origin https://github.com/YOUR_USERNAME/tm_loc_mt.git

# Push to GitHub
git push -u origin master
```

### .gitignore Rules
- Ignores: Python cache, logs, temp files, .env
- Keeps: Source code, documentation, config examples
- Keeps: Excel data files (localization.xlsx)

### Common Workflow
```bash
# 1. Make changes to code
# 2. Test locally with: ./run_translation.bat
# 3. Commit: git commit -am "what I changed"
# 4. Push: git push
```
