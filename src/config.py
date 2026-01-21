"""Configuration management for the translation pipeline."""

from pathlib import Path
from dataclasses import dataclass
from typing import List
import os
from dotenv import load_dotenv


# ============================================================================
# MODIFY THESE SETTINGS TO CHANGE TRANSLATION BEHAVIOR
# ============================================================================

# Target language for translation
TARGET_LANG = "Portuguese_BR"

# Column name for target language translations in Excel
TARGET_COL = "Portuguese"

# Which sheets to translate (modify this list to control which sheets are processed)
SHEETS_TO_TRAD = [
#    "Default",
#    "Sandbox",
#    "GEO",
#    "TENNIS",
#    "MANAGER",
#    "EQUIP",
#    "TRAINING",
    "MATCH",
    "STAFF",
#    "INBOX",
#    "PLAYER",
#    "ACADEMY",
#    "SCENARIOS",
#    "TUTO",
#    "FC",
#    "MEDIA",
#    "LD_INBOX",
#    "LD_RADIO",
#    "UI",
#    "WORLD",
#    "LD_BRIEFING",
#    "LD_OBJ_CA",
#    "LD_OBJ_PLY",
#    "LD_RPT_TRAIN",
#    "LD_TALK",
#    "LD_ADVICES",
#    "MP_UI",
#    "MP_ATT",
#    "MP_NEWS",
#    "MP_SKILLS",
#    "MP_TUTO"
]

# Batch size for API calls (number of segments per batch)
BATCH_SIZE = 50

# Rate limiting: cooldown seconds between batches (prevents API throttling)
BATCH_COOLDOWN_SECONDS = 22.0

# Use Gemini API (True) or OpenAI API (False)
USE_GEMINI = True

GEMINI_MODEL = "gemini-2.5-flash-lite"
OPENAI_MODEL = "gpt-4o-mini"

# ============================================================================
# END OF CONFIGURATION SECTION
# ============================================================================


@dataclass
class APIConfig:
    """API configuration for OpenAI and Gemini."""
    use_gemini: bool = True
    gemini_model: str = GEMINI_MODEL
    openai_model: str = OPENAI_MODEL
    gemini_api_key: str = ""
    openai_api_key: str = ""
    max_retries_openai: int = 5
    max_retries_gemini: int = 5
    rate_limit_wait: float = 25.0
    
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
    
    def __post_init__(self):
        if self.sheets_to_translate is None:
            self.sheets_to_translate = SHEETS_TO_TRAD.copy()


@dataclass
class ExcelConfig:
    """Excel file configuration."""
    excel_path: str = "localization.xlsx"
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

