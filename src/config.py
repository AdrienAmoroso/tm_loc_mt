"""Configuration management for the translation pipeline."""

from pathlib import Path
from dataclasses import dataclass
from typing import List
import os
from dotenv import load_dotenv

from settings_manager import load_settings

# Load settings from settings.ini (or run setup wizard if not exists)
_settings = load_settings()

# ============================================================================
# CONFIGURATION (now loaded from settings.ini)
# ============================================================================

TARGET_LANG = _settings["target_language"]
TARGET_COL = _settings["target_column"]
SHEETS_TO_TRAD = _settings["sheets"]
BATCH_SIZE = _settings["batch_size"]
BATCH_COOLDOWN_SECONDS = _settings["batch_cooldown_seconds"]
USE_GEMINI = _settings["provider"] == "gemini"
EXCEL_FILE = _settings["excel_file"]
AI_PROMPT = _settings.get("ai_prompt", "")

GEMINI_MODEL = "gemini-2.5-flash-lite"
OPENAI_MODEL = "gpt-4o-mini"

# Load AI prompt from file if specified in settings
if not AI_PROMPT and _settings.get("ai_prompt_file"):
    prompt_file = Path(_settings.get("ai_prompt_file"))
    if prompt_file.exists():
        AI_PROMPT = prompt_file.read_text(encoding="utf-8").strip()

# ============================================================================
# END OF CONFIGURATION SECTION
# ============================================================================


@dataclass
class APIConfig:
    """API configuration for OpenAI and Gemini."""
    use_gemini: bool = USE_GEMINI
    gemini_model: str = GEMINI_MODEL
    openai_model: str = OPENAI_MODEL
    gemini_api_key: str = ""
    openai_api_key: str = ""
    max_retries_openai: int = _settings["max_retries"]
    max_retries_gemini: int = _settings["max_retries"]
    rate_limit_wait: float = _settings["rate_limit_wait"]
    
    def validate(self) -> None:
        """Validate that required API keys are configured."""
        if self.use_gemini:
            if not self.gemini_api_key:
                raise RuntimeError("GEMINI_API_KEY not found in environment variables")
        else:
            if not self.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY not found in environment variables")


@dataclass
class TranslationConfig:
    """Translation settings."""
    source_lang: str = "English"
    target_lang: str = TARGET_LANG
    target_col: str = TARGET_COL
    sheets_to_translate: List[str] = None
    batch_size: int = BATCH_SIZE
    batch_cooldown_seconds: float = BATCH_COOLDOWN_SECONDS
    ai_prompt: str = AI_PROMPT
    
    def __post_init__(self):
        if self.sheets_to_translate is None:
            self.sheets_to_translate = SHEETS_TO_TRAD.copy()


@dataclass
class ExcelConfig:
    """Excel file configuration."""
    excel_path: str = EXCEL_FILE
    keys_column: str = "Keys"
    comment_column: str = "$comment"
    donottranslate_column: str = "$donottranslate"
    
    @property
    def excel_path_obj(self) -> Path:
        """Get Excel path as Path object."""
        return Path(self.excel_path)


@dataclass
class LoggingConfig:
    """Logging configuration."""
    logs_dir: Path = None
    level: str = "INFO"
    
    def __post_init__(self):
        if self.logs_dir is None:
            self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)


class Config:
    """Main configuration container."""
    
    def __init__(self):
        load_dotenv()
        
        self.api = APIConfig(
            use_gemini=USE_GEMINI,
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        )
        
        self.translation = TranslationConfig()
        self.excel = ExcelConfig()
        self.logging = LoggingConfig()
        
        self.api.validate()
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables (overrides defaults)."""
        config = cls()
        
        # Allow environment variables to override defaults
        if target_lang := os.getenv("TARGET_LANG"):
            config.translation.target_lang = target_lang
            config.translation.target_col = target_lang
        
        if sheets := os.getenv("SHEETS_TO_TRAD"):
            config.translation.sheets_to_translate = [s.strip() for s in sheets.split(",")]
        
        if batch_size := os.getenv("BATCH_SIZE"):
            config.translation.batch_size = int(batch_size)
        
        return config

