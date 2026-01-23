# Localization Translation Tool

An automated, intelligent machine translation system for translating Excel-based localization files using AI APIs (OpenAI GPT-4 or Google Gemini).

## Overview

This tool automates the translation of structured localization data from Excel files. It processes key-value pairs while preserving technical placeholders, handling edge cases with validation, and providing comprehensive logging. Perfect for translating application text, websites, games, or any domain-specific content.

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

The batch script at `scripts/run_translation.bat` will **only work after you complete steps 1-3**. For the first run, use Option B below:

#### Option A: Using Batch Script (After first run)
Once setup is complete, you can double-click:
```
scripts/run_translation.bat
```

#### Option B: Using Python
```powershell
python translate_loc.py
```

The tool will create `settings.ini` with your preferences. Answer these questions:
- **Target Language:** e.g., `Portuguese_BR`, `French`, `Spanish`
- **Target Column Name:** Column header name in your Excel file (e.g., `Portuguese`)
- **Sheets to Translate:** Which sheets from your workbook to process
- **API Provider:** Choose Gemini (recommended, free tier) or OpenAI
- **Batch Size:** Default is 50 (higher = faster but higher risk of timeouts)

**Setup complete!** Your configuration is saved to `settings.ini`.

### Results

After translation completes, check:
- **Excel file:** Your `localization.xlsx` is updated with translations
- **Status report:** `logs/mt_keys_*.csv` - See which segments succeeded, failed, or were copied
- **Detailed log:** `logs/mt_run_*.log` - For debugging

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
batch_cooldown_seconds = 22.0

[API]
provider = gemini
max_retries = 5
rate_limit_wait = 25.0

[Excel]
excel_file = localization.xlsx
```

### Custom AI Prompts

By default, the tool uses a generic translation prompt suitable for any domain. To customize the AI's translation behavior for your specific needs:

#### Option 1: Using a Custom Prompt File (Recommended)

Best for complex, multi-line prompts or domain-specific instructions.

**Step 1:** Create or edit `custom_prompt.txt` in the project root with your translation instructions:

```
You are translating for a video game called "Tennis Manager".

You translate text from {source} to {target}.

RULES:
- Keep UI text concise and clear
- Use natural language for dialogue
- Preserve technical tokens like __VAR0__, __VAR1__, etc.
- Maintain character voice in translations
- Do NOT add new meaning or omit information

RESPONSE FORMAT
Answer as valid JSON:
{
  "translations": [
    { "key": "KEY_FROM_INPUT", "text": "Translated text here" }
  ]
}
```

**Important:** Keep the `{source}` and `{target}` placeholders - they're automatically replaced with the actual languages.

**Step 2:** Enable the prompt file in `settings.ini`:

```ini
[Translation]
ai_prompt_file = custom_prompt.txt
```

**Step 3:** Run the tool - it will use your custom prompt automatically.

#### Option 2: Inline Prompt (Simple Cases)

For short, simple prompts without special characters, add directly to `settings.ini`:

```ini
[Translation]
ai_prompt = Translate video game UI text concisely. Keep it natural and clear.
```

#### Reset to Default Prompt

Comment out both options in `settings.ini`:

```ini
[Translation]
# ai_prompt_file = custom_prompt.txt
# ai_prompt = 
```

#### Verify Which Prompt Is Being Used

To check that your custom prompt is loaded:

1. **Check settings.ini** - Make sure `ai_prompt_file` is uncommented:
   ```ini
   ai_prompt_file = custom_prompt.txt  # Should NOT have # at the start
   ```

2. **Check the custom_prompt.txt file exists** - It should be in the project root (same level as settings.ini)

3. **Look at the first translation's quality** - If your custom instructions are being used, you'll see results matching your prompt's rules

4. **Check logs** - The detailed logs in `logs/mt_run_*.log` show which segments were translated and any errors

---

## Features
Delete `settings.ini` and run the tool again - it will ask setup questions.

---

## Features

- **Batch Translation:** Processes segments efficiently in configurable batches
- **Placeholder Protection:** Preserves `{[variable]}` and `<tag>` patterns exactly
- **Dual AI Support:** Switch between Gemini and OpenAI with one setting
- **Smart Validation:** Ensures all tokens are preserved in correct order
- **Gap Filling:** Auto-detects and re-translates missed segments
- **DoNotTranslate Support:** Mark cells with `$donottranslate` flag to copy unchanged
- **Custom Prompts:** Configure domain-specific translation rules
- **Clean UI:** Progress bars with no log clutter in console
- **Comprehensive Logging:** Detailed files for debugging and analysis

---

## How It Works

1. **Load** Excel segments from specified sheets
2. **Filter** by translation needs:
   - Skip if source is empty
   - Skip if target already filled
   - Copy if marked with `$donottranslate`
   - Translate if needs translation
3. **Protect** placeholders (e.g., `{[variable]}` → `__VAR0__`)
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
├── .env                           # API keys (create manually, gitignored)
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
- **Source column:** Your original text
- **Target column:** Translated text (filled by the tool)

### Status CSV (`logs/mt_keys_*.csv`)
Status codes:
- `OK` - Successfully translated
- `COPIED_SOURCE` - Marked `$donottranslate`, source copied
- `NO_TRANSLATION` - API returned empty translation
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

### "ModuleNotFoundError: No module named 'rich'" (when running .bat file)
The batch file couldn't find the virtual environment packages.

**Solution:** Make sure you completed the setup properly:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then try the .bat file again.

### "Virtual environment not found"
The `.venv` folder doesn't exist.

**Solution:** Run these commands in PowerShell (from project root):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
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


## Excel Format

Your `localization.xlsx` should have this structure:

| Keys | [Source Language] | [Target Language] | $comment | $donottranslate |
|------|-------------------|-------------------|----------|-----------------|
| key_1 | English text | | Optional context | ✓ |
| key_2 | Another text | | | |
| key_3 | Text | | | |

**Columns:**
- `Keys` - Unique identifier (required)
- Source column - Original language text (required)
- Target column - Where translations go (created if missing)
- `$comment` - Context for translators (optional)
- `$donottranslate` - Mark with ✓ to skip translation (optional)

---

## For Developers

### Adding Support for a New API

1. Update `TranslationService` in `src/translation_service.py`
2. Add API configuration to `src/config.py`
3. Update settings template in `settings.ini`
4. Add environment variable in `.env`

### Modifying Translation Behavior

Edit `src/translation_service.py`:
- `build_system_prompt()` - AI instructions
- `build_user_content()` - Data formatting
- `translate_batch()` - API interaction

### Custom Validation

Edit `src/validation_service.py`:
- `validate_placeholder_preservation()` - Token checking
- Add custom rules as needed

---

## Use Cases

- **Video Games:** Localize UI, dialogue, and documentation
- **Software Applications:** Translate menus, help text, and settings
- **E-commerce:** Translate product descriptions and marketing copy
- **Websites:** Localize content pages and user interfaces
- **Documentation:** Translate technical manuals and guides
- **Mobile Apps:** Translate user-facing strings

---

## License

Open source project available for community use.

## Author

Adrien Amoroso  
[GitHub Profile](https://github.com/AdrienAmoroso)

---

**Status:** Production Ready  
**Last Updated:** January 23, 2026  
**Python Version:** 3.13+
