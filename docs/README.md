# Localization Translation Tool

> AI-powered batch translation pipeline for Excel-based localization files with placeholder preservation and validation.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../LICENSE)
[![Tests](https://img.shields.io/badge/tests-42%20passed-brightgreen.svg)](../tests/)
[![Ruff](https://img.shields.io/badge/linting-Ruff-purple.svg)](https://docs.astral.sh/ruff/)
[![CI](https://github.com/AdrienAmoroso/tm_loc_mt/actions/workflows/ci.yml/badge.svg)](https://github.com/AdrienAmoroso/tm_loc_mt/actions)

---

## What It Demonstrates

- **API Integration** — Dual support for OpenAI GPT-4 and Google Gemini with retry logic and rate limiting
- **Data Pipeline Architecture** — Batch processing with validation, gap-filling, and rollback safety
- **Placeholder Protection** — Regex-based token extraction/restoration preserving `{[var]}` and `<tag>` patterns
- **Clean Code Practices** — Service-oriented architecture, dataclasses, type hints, comprehensive logging
- **Testing** — 42 unit tests with pytest covering core validation logic (100% coverage on critical modules)
- **CI/CD** — GitHub Actions pipeline with Ruff linting, pytest, and build verification
- **User Experience** — Interactive setup wizard, Rich CLI progress bars, INI-based configuration

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.13 |
| **AI APIs** | OpenAI GPT-4o-mini, Google Gemini 2.5 |
| **Data** | pandas, openpyxl |
| **CLI** | Rich |
| **Config** | python-dotenv, configparser |
| **Testing** | pytest, pytest-cov |
| **Linting** | Ruff |

---

## Quickstart

```bash
# 1. Setup environment
python -m venv .venv && .\.venv\Scripts\Activate.ps1 && pip install -r requirements.txt

# 2. Configure API key
echo "GEMINI_API_KEY=your_key_here" > .env

# 3. Run (interactive setup on first run)
python translate_loc.py
```

---

## Architecture

```
├── src/
│   ├── localization_engine.py   # Orchestrator — batch processing, gap-filling
│   ├── translation_service.py   # AI API calls with retry logic
│   ├── validation_service.py    # Placeholder preservation checks
│   ├── excel_service.py         # Excel I/O operations
│   ├── settings_manager.py      # Interactive setup wizard
│   ├── config.py                # Configuration loader
│   ├── models.py                # Segment dataclass
│   ├── utils.py                 # PlaceholderManager utility
│   └── html_report_service.py   # HTML report generation
├── tests/
│   ├── test_models.py           # 15 tests for data models
│   ├── test_placeholder_manager.py  # 20 tests for placeholder logic
│   └── test_validation_service.py   # 7 tests for validation
└── .github/workflows/ci.yml     # CI pipeline
```

**Data Flow:**
```
Excel → Load Segments → Protect Placeholders → Batch Translate → Validate → Restore → Write Excel
```

---

## Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Run linting
ruff check src/ tests/
```

**Results:** ✅ 42 tests passing | 100% coverage on models, utils, validation_service

---

## CI Pipeline

**GitHub Actions Workflow:** `.github/workflows/ci.yml`

| Stage | Tools | Description |
|-------|-------|-------------|
| **lint** | Ruff | Code linting + format check |
| **test** | pytest + coverage | 42 unit tests with coverage report |
| **build** | Python imports | Verify all modules load correctly |

---

## Roadmap

- [ ] **Web UI** — Flask dashboard for non-technical users
- [ ] **Async Processing** — Parallel batch translation for 3x speed
- [ ] **Translation Memory** — Cache repeated segments to reduce API costs

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Batch Processing** | Configurable batch sizes (default: 50 segments) |
| **Placeholder Safety** | `{[player]}` → `__VAR0__` → translated → `{[player]}` |
| **Gap Filling** | Auto-detects and retries failed translations |
| **Custom Prompts** | Domain-specific AI instructions via external file |
| **Status Reports** | CSV logs with OK / MISSING_TOKENS / COPIED_SOURCE |
| **HTML Reports** | Visual summary with per-sheet breakdown |

---

## Example

**Input:**
| Keys | English | Portuguese |
|------|---------|------------|
| welcome | Hello, {[player]}! | |

**Output:**
| Keys | English | Portuguese |
|------|---------|------------|
| welcome | Hello, {[player]}! | Olá, {[player]}! |

---

## Configuration

```ini
# settings.ini
[Translation]
target_language = Portuguese
sheets = UI, DIALOGUE
batch_size = 50
ai_prompt_file = custom_prompt.txt

[API]
provider = gemini  # or 'openai'
max_retries = 5
```

---

## Author

**Adrien Amoroso** — [GitHub](https://github.com/AdrienAmoroso)

---

*Built with Python • Powered by AI • Production Ready*
