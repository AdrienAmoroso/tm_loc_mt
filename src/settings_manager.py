"""Settings management with INI file and interactive setup wizard."""

import configparser
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()

SETTINGS_FILE = Path(__file__).parent.parent / "settings.ini"

# Available sheets in the localization file
AVAILABLE_SHEETS = [
    "Default",
    "Sandbox",
    "GEO",
    "TENNIS",
    "MANAGER",
    "EQUIP",
    "TRAINING",
    "MATCH",
    "STAFF",
    "INBOX",
    "PLAYER",
    "ACADEMY",
    "SCENARIOS",
    "TUTO",
    "FC",
    "MEDIA",
    "LD_INBOX",
    "LD_RADIO",
    "UI",
    "WORLD",
    "LD_BRIEFING",
    "LD_OBJ_CA",
    "LD_OBJ_PLY",
    "LD_RPT_TRAIN",
    "LD_TALK",
    "LD_ADVICES",
    "MP_UI",
    "MP_ATT",
    "MP_NEWS",
    "MP_SKILLS",
    "MP_TUTO",
]


class SettingsManager:
    """Manage translation settings from INI file."""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.settings_path = SETTINGS_FILE

    def load(self) -> dict:
        """Load settings from INI file."""
        if not self.settings_path.exists():
            console.print("[yellow]settings.ini not found. Running setup wizard...[/yellow]\n")
            self.run_setup_wizard()

        self.config.read(self.settings_path)
        return self._parse_config()

    def _parse_config(self) -> dict:
        """Parse INI config into settings dictionary."""
        settings = {
            "target_language": self.config.get("Translation", "target_language"),
            "target_column": self.config.get("Translation", "target_column"),
            "sheets": [s.strip() for s in self.config.get("Translation", "sheets").split(",")],
            "batch_size": self.config.getint("Translation", "batch_size"),
            "batch_cooldown_seconds": self.config.getfloat("Translation", "batch_cooldown_seconds"),
            "provider": self.config.get("API", "provider").lower(),
            "max_retries": self.config.getint("API", "max_retries"),
            "rate_limit_wait": self.config.getfloat("API", "rate_limit_wait"),
            "excel_file": self.config.get("Excel", "excel_file"),
        }

        # Optional: ai_prompt or ai_prompt_file
        if self.config.has_option("Translation", "ai_prompt_file"):
            settings["ai_prompt_file"] = self.config.get("Translation", "ai_prompt_file")
        else:
            settings["ai_prompt_file"] = None

        if self.config.has_option("Translation", "ai_prompt"):
            settings["ai_prompt"] = self.config.get("Translation", "ai_prompt")
        else:
            settings["ai_prompt"] = ""

        self._validate_settings(settings)
        return settings

    def _validate_settings(self, settings: dict) -> None:
        """Validate settings values."""
        # Validate target language
        if not settings["target_language"].strip():
            raise ValueError("target_language cannot be empty")

        # Validate target column
        if not settings["target_column"].strip():
            raise ValueError("target_column cannot be empty")

        # Validate sheets
        if not settings["sheets"]:
            raise ValueError("At least one sheet must be selected")

        invalid_sheets = [s for s in settings["sheets"] if s not in AVAILABLE_SHEETS]
        if invalid_sheets:
            raise ValueError(f"Invalid sheets: {invalid_sheets}. Available: {AVAILABLE_SHEETS}")

        # Validate batch size
        if settings["batch_size"] < 1 or settings["batch_size"] > 100:
            raise ValueError("batch_size must be between 1 and 100")

        # Validate provider
        if settings["provider"] not in ["gemini", "openai"]:
            raise ValueError("provider must be 'gemini' or 'openai'")

        # Validate retries
        if settings["max_retries"] < 1:
            raise ValueError("max_retries must be at least 1")

    def run_setup_wizard(self) -> None:
        """Interactive setup wizard for first-time configuration."""
        title = Text("Tennis Manager Translation - Initial Setup", style="bold cyan")
        console.print(Panel(title, border_style="cyan"))
        console.print()

        # Target Language
        target_lang = Prompt.ask(
            "[bold]Target Language[/bold]", default="English", show_default=True
        )

        # Target Column
        target_col = Prompt.ask(
            "[bold]Target Column Name[/bold] (in Excel)", default="English", show_default=True
        )

        # Sheets Selection
        console.print("\n[bold]Available Sheets:[/bold]")
        for i, sheet in enumerate(AVAILABLE_SHEETS, 1):
            console.print(f"  {i:2}. {sheet}")

        sheets_input = Prompt.ask(
            "[bold]Sheets to translate[/bold] (comma-separated)",
            default="MATCH, STAFF",
            show_default=True,
        )

        sheets = self._parse_sheets_input(sheets_input)

        # Batch Size
        batch_size = Prompt.ask("[bold]Batch Size[/bold]", default="50", show_default=True)

        try:
            batch_size = int(batch_size)
            if batch_size < 1 or batch_size > 100:
                raise ValueError()
        except ValueError:
            console.print("[red]Invalid batch size, using default 50[/red]")
            batch_size = 50

        # API Provider
        console.print("\n[bold]API Providers:[/bold]")
        console.print("  1. Gemini")
        console.print("  2. OpenAI")

        provider = Prompt.ask(
            "[bold]Choose API[/bold]",
            choices=["1", "2", "gemini", "openai"],
            default="1",
            show_default=True,
        )

        provider = "gemini" if provider in ["1", "gemini"] else "openai"

        # Save settings
        self._save_settings(target_lang, target_col, sheets, batch_size, provider)

        console.print("\n[bold green]Setup complete![/bold green]")
        console.print(f"[dim]Settings saved to: {self.settings_path}[/dim]\n")

    def _parse_sheets_input(self, sheets_input: str) -> list[str]:
        """Parse sheet input (numbers or names)."""
        sheets = []
        for item in sheets_input.split(","):
            item = item.strip()

            # Try as number (1-indexed)
            try:
                idx = int(item) - 1
                if 0 <= idx < len(AVAILABLE_SHEETS):
                    sheets.append(AVAILABLE_SHEETS[idx])
                    continue
            except ValueError:
                pass

            # Try as sheet name
            if item in AVAILABLE_SHEETS:
                sheets.append(item)
                continue

            # If nothing worked, try to find partial match
            matches = [s for s in AVAILABLE_SHEETS if s.lower() == item.lower()]
            if matches:
                sheets.append(matches[0])
                continue

            console.print(f"[yellow]Warning: Sheet '{item}' not found, skipping[/yellow]")

        return sheets or [AVAILABLE_SHEETS[0]]  # Default fallback

    def _save_settings(
        self, target_lang: str, target_col: str, sheets: list[str], batch_size: int, provider: str
    ) -> None:
        """Save settings to INI file."""
        config = configparser.ConfigParser()

        config["Translation"] = {
            "target_language": target_lang,
            "target_column": target_col,
            "sheets": ", ".join(sheets),
            "batch_size": str(batch_size),
            "batch_cooldown_seconds": "22.0",
            "# ai_prompt_file": "custom_prompt.txt",
        }

        config["API"] = {
            "provider": provider,
            "max_retries": "5",
            "rate_limit_wait": "25.0",
        }

        config["Excel"] = {
            "excel_file": "localization.xlsx",
        }

        with self.settings_path.open("w") as f:
            config.write(f)


def load_settings() -> dict:
    """Load settings from INI file (create if needed)."""
    manager = SettingsManager()
    return manager.load()
