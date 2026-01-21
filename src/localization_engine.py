"""Main orchestration engine for the translation pipeline."""

import logging
import time
from pathlib import Path
from typing import List, Dict

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.console import Console

from models import Segment, TranslationResult
from config import Config
from excel_service import ExcelService
from translation_service import TranslationService
from validation_service import ValidationService
from utils import PlaceholderManager
from html_report_service import HTMLReportService

logger = logging.getLogger(__name__)
console = Console()


class LocalizationEngine:
    """Main orchestrator for the translation pipeline."""
    
    def __init__(self, config: Config, keys_log_path: Path):
        self.config = config
        self.keys_log_path = keys_log_path
        self.excel_service = ExcelService(config)
        self.translation_service = TranslationService(config)
        self.validation_service = ValidationService()
    
    def run(self) -> None:
        """Execute the full translation pipeline."""
        logger.info(f"=== Starting translation for {self.config.translation.target_lang} ===")
        run_id = self.keys_log_path.stem.split("_", 2)[-1]  # Extract run_id from filename
        
        try:
            existing_sheets = self.excel_service.get_existing_sheets()
            total_translated = 0
            total_gaps_filled = 0
            
            sheets_to_process = [s for s in self.config.translation.sheets_to_translate if s in existing_sheets]
            
            if not sheets_to_process:
                console.print("[bold red] No valid sheets to process[/bold red]")
                logger.error("No valid sheets to process")
                return
            
            # Main translation phase
            console.print(f"\n[bold cyan] Starting translation ({len(sheets_to_process)} sheets)[/bold cyan]")
            for sheet_name in sheets_to_process:
                translated = self._translate_sheet(sheet_name)
                total_translated += translated
            
            console.print(f"[green] Translated {total_translated} segments[/green]\n")
            logger.info(f"Total segments translated: {total_translated}")
            
            # Gap-filling phase
            console.print(f"[bold cyan] Starting gap-filling phase[/bold cyan]")
            for sheet_name in sheets_to_process:
                gaps_filled = self._fill_gaps_in_sheet(sheet_name)
                total_gaps_filled += gaps_filled
            
            if total_gaps_filled > 0:
                console.print(f"[green] Filled {total_gaps_filled} gaps[/green]\n")
            else:
                console.print(f"[yellow] No gaps found[/yellow]\n")
            
            logger.info(f"Total gaps filled: {total_gaps_filled}")
            logger.info(f"=== Translation complete ===")
            
            # Generate HTML report
            html_path = HTMLReportService.generate_report(self.keys_log_path, run_id, self.config)
            console.print(f"\n[bold cyan] Report generated: [/bold cyan][cyan]{html_path.name}[/cyan]")
            logger.info(f"HTML report generated: {html_path}")
        
        except Exception as e:
            console.print(f"[bold red] Fatal error: {e}[/bold red]")
            logger.error(f"[Main] Fatal error: {e}", exc_info=True)
            raise
    
    def _translate_sheet(self, sheet_name: str) -> int:
        """Translate a single sheet."""
        logger.info(f"--- Processing sheet '{sheet_name}' ---")
        
        # Load segments
        segments = self.excel_service.load_segments_from_sheet(sheet_name)
        segments_to_translate = [s for s in segments if s.needs_translation()]
        
        if not segments_to_translate:
            logger.info(f"[{sheet_name}] No segments to translate")
            return 0
        
        logger.debug(f"[{sheet_name}] {len(segments_to_translate)} segments to translate")
        
        # Build batches
        batches = self._build_batches(segments_to_translate)
        logger.debug(f"[{sheet_name}] {len(batches)} batches created")
        
        # Process batches with progress bar
        all_translations = {}
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[cyan]{sheet_name}[/cyan]"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Translating {sheet_name}", total=len(batches))
            
            for i, batch in enumerate(batches, start=1):
                logger.debug(f"[{sheet_name}] Processing batch {i}/{len(batches)} ({len(batch)} segments)")
                
                try:
                    batch_translations = self._process_batch(sheet_name, batch)
                    all_translations.update(batch_translations)
                    
                    progress.update(task, advance=1)
                    
                    # Cooldown between batches
                    if i < len(batches):
                        logger.debug(f"[{sheet_name}] Cooldown {self.config.translation.batch_cooldown_seconds}s...")
                        time.sleep(self.config.translation.batch_cooldown_seconds)
                
                except Exception as e:
                    logger.error(f"[{sheet_name}] Batch {i} failed: {e}")
                    progress.update(task, advance=1)
                    # Continue with next batch instead of stopping
                    continue
        
        # Write to Excel
        if all_translations:
            self.excel_service.write_translations(sheet_name, all_translations)
        
        logger.info(f"[{sheet_name}] Translated {len(all_translations)} segments")
        return len(all_translations)
    
    def _process_batch(self, sheet_name: str, batch: List[Segment]) -> Dict[int, str]:
        """Process a single batch of segments."""
        result = {}
        
        try:
            # Get translations from API
            translations = self.translation_service.translate_batch(batch)
            
            # Process each segment
            for seg in batch:
                translated_text = translations.get(seg.key, "")
                
                if not translated_text or not translated_text.strip():
                    logger.debug(f"[MT] No translation for key={seg.key}")
                    self._log_key(seg.sheet, seg.key, seg.row_idx, "NO_TRANSLATION")
                    continue
                
                # Validate placeholders
                protected_source, placeholder_map = PlaceholderManager.protect(seg.source_text)
                validation = self.validation_service.validate_translation(
                    seg, translated_text, placeholder_map
                )
                
                if not validation.is_valid:
                    logger.warning(
                        f"[MT] Validation failed for key={seg.key}: "
                        f"missing={validation.missing_tokens}, out_of_order={validation.out_of_order}"
                    )
                    self._log_key(
                        seg.sheet, seg.key, seg.row_idx,
                        "TOKENS_OUT_OF_ORDER" if validation.out_of_order else "MISSING_TOKENS"
                    )
                    continue
                
                # Restore placeholders and store result
                final_text = PlaceholderManager.restore(translated_text, placeholder_map)
                result[seg.row_idx] = final_text
                
                logger.debug(f"[MT] Translated key={seg.key} row={seg.row_idx}")
                self._log_key(seg.sheet, seg.key, seg.row_idx, "OK")
        
        except Exception as e:
            logger.error(f"[Batch] Error processing batch: {e}")
        
        return result
    
    def _fill_gaps_in_sheet(self, sheet_name: str) -> int:
        """Find and fill gaps in a sheet."""
        logger.debug(f"[Verify] Checking for gaps in '{sheet_name}'...")
        
        segments = self.excel_service.load_segments_from_sheet(sheet_name)
        gaps = [s for s in segments if s.needs_translation()]
        
        if not gaps:
            logger.debug(f"[Verify] No gaps in '{sheet_name}'")
            return 0
        
        logger.info(f"[Verify] Found {len(gaps)} gaps in '{sheet_name}', attempting to fill...")
        
        gap_batches = self._build_batches(gaps)
        total_filled = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[yellow]{sheet_name} (gaps)[/yellow]"),
            BarColumn(),
            MofNCompleteColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Filling gaps in {sheet_name}", total=len(gap_batches))
            
            for i, batch in enumerate(gap_batches, start=1):
                logger.debug(f"[Verify] Gap batch {i}/{len(gap_batches)}")
                
                try:
                    gap_translations = self._process_batch(sheet_name, batch)
                    
                    if gap_translations:
                        self.excel_service.write_translations(sheet_name, gap_translations)
                        total_filled += len(gap_translations)
                    
                    progress.update(task, advance=1)
                    
                    if i < len(gap_batches):
                        time.sleep(self.config.translation.batch_cooldown_seconds)
                
                except Exception as e:
                    logger.error(f"[Verify] Gap batch {i} failed: {e}")
                    progress.update(task, advance=1)
                    continue
        
        logger.info(f"[Verify] Filled {total_filled} gaps in '{sheet_name}'")
        return total_filled
    
    def _build_batches(self, segments: List[Segment]) -> List[List[Segment]]:
        """Split segments into batches."""
        batches = []
        batch_size = self.config.translation.batch_size
        
        for i in range(0, len(segments), batch_size):
            batches.append(segments[i:i + batch_size])
        
        return batches
    
    def _log_key(self, sheet: str, key: str, row_idx: int, status: str) -> None:
        """Log translation status for a key."""
        is_new_file = not self.keys_log_path.exists()
        
        with self.keys_log_path.open("a", encoding="utf-8") as f:
            if is_new_file:
                f.write("sheet,key,row_idx,target_lang,status\n")
            f.write(f"{sheet},{key},{row_idx},{self.config.translation.target_lang},{status}\n")
