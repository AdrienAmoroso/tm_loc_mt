#!/usr/bin/env python3
"""
Tennis Manager 25 Localization Translation Pipeline

A machine translation system for localizing the Tennis Manager 25 video game
from English to multiple target languages using AI APIs (OpenAI/Gemini).

Features:
- Batch translation with placeholder preservation
- Validation of technical tokens (placeholders)
- Gap-filling for missed translations
- Comprehensive logging and status tracking
- Robust error handling with retries
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from config import Config
from localization_engine import LocalizationEngine

console = Console()


def setup_logging(config: Config) -> str:
    """Configure logging for the application. Returns run_id."""
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = config.logging.logs_dir / f"mt_run_{run_id}.log"
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    
    # File handler: detailed logs (all levels)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler: only show WARNING and ERROR to avoid cluttering UI
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(detailed_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Suppress verbose third-party loggers
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("google").setLevel(logging.ERROR)
    logging.getLogger("openai").setLevel(logging.ERROR)
    
    return run_id


def main() -> int:
    """Main entry point."""
    try:
        # Load configuration
        config = Config.from_env()
        
        # Setup logging
        run_id = setup_logging(config)
        logger = logging.getLogger(__name__)
        
        # Display nice header
        title = Text("🎾 Tennis Manager 25 - Localization Translation", style="bold cyan")
        console.print(Panel(title, border_style="cyan"))
        
        # Display configuration
        config_text = Text()
        config_text.append(f"Target Language: ", style="bold")
        config_text.append(f"{config.translation.target_lang}\n", style="green")
        config_text.append(f"Sheets to Translate: ", style="bold")
        config_text.append(f"{', '.join(config.translation.sheets_to_translate)}\n", style="green")
        config_text.append(f"Batch Size: ", style="bold")
        config_text.append(f"{config.translation.batch_size}", style="green")
        
        console.print(Panel(config_text, title="Configuration", border_style="yellow"))
        
        # Create run log
        keys_log_path = config.logging.logs_dir / f"mt_keys_{run_id}.csv"
        
        logger.info("=" * 80)
        logger.info(f"Target Language: {config.translation.target_lang}")
        logger.info(f"Sheets to Translate: {config.translation.sheets_to_translate}")
        logger.info("=" * 80)
        
        # Run translation pipeline
        engine = LocalizationEngine(config, keys_log_path)
        engine.run()
        
        # Display success message
        success_text = Text()
        success_text.append("✅ Translation pipeline completed successfully!\n", style="bold green")
        success_text.append(f"Log file: ", style="dim")
        success_text.append(f"logs/mt_run_{run_id}.log\n", style="cyan")
        success_text.append(f"Status file: ", style="dim")
        success_text.append(f"logs/mt_keys_{run_id}.csv", style="cyan")
        
        console.print(Panel(success_text, border_style="green"))
        
        logger.info("=" * 80)
        logger.info("Translation pipeline completed successfully")
        logger.info("=" * 80)
        return 0
    
    except KeyboardInterrupt:
        console.print("\n[bold red]⚠️  Translation interrupted by user[/bold red]")
        logger.warning("Translation interrupted by user")
        return 130
    
    except Exception as e:
        console.print(f"\n[bold red]❌ Fatal error: {e}[/bold red]")
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
