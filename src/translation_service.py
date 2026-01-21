"""API service for machine translation."""

import json
import logging
import time
from typing import List, Dict

from google import genai
from google.genai import types
from openai import OpenAI

from models import Segment
from config import Config
from utils import PlaceholderManager

logger = logging.getLogger(__name__)


class TranslationService:
    """Handles API calls to OpenAI or Gemini for translation."""
    
    def __init__(self, config: Config):
        self.config = config
        
        if config.api.use_gemini:
            self.client = genai.Client(api_key=config.api.gemini_api_key)
        else:
            self.client = OpenAI(api_key=config.api.openai_api_key)
    
    def build_system_prompt(self) -> str:
        """Build the system prompt for the AI model."""
        source = self.config.translation.source_lang
        target = self.config.translation.target_lang
        
        return f"""
You are a professional localization engine for the video game "Tennis Manager 25",
a realistic tennis management game on PC. The player is the manager of a tennis academy
and manages up to 8 players while meeting sporting and financial objectives.

You translate in-game text from {source} to {target}.

GENERAL RULES
1. Technical tokens:
   - Never modify, translate or reorder technical tokens like __VAR0__, __VAR1__, __TAG0__, etc.
   - They represent placeholders or markup and must remain exactly as they are and in the same position.
   - If the source contains tokens like __TAG0__, __TAG1__, etc., the translation MUST contain exactly the same tokens, in the same order. Do not remove them, even if you change the wording.

2. Source format:
   - Texts come from an Excel localization sheet.
   - Each entry has:
     - a 'key' (identifier),
     - a 'sheet' name (e.g. "UI", "Staff", "Match", "Media", "Tuto", "Ld_talk", "Ld_advices", etc.),
     - an optional 'comment' that gives context.
   - Use the 'sheet' and 'comment' to adapt the tone.

3. Style and tone:
   - Overall tone: natural and fluent, consistent with a serious sports management game.
   - For sheets like "UI", "Default", "Geo", "Tennis", "Manager", "Equip":
     - These are UI labels or short texts → keep translations as short and clear as possible.
   - For "Tuto" and other long tutorial texts:
     - You may use slightly longer, didactic sentences, but still concise.
   - For "Match" and "Ld_radio":
     - These are live match comments → dynamic, natural speech, like a commentator.

4. Gender handling (_M / _F keys):
   - If the key ends with "_M", the text refers to a male character.
   - If the key ends with "_F", the text refers to a female character.
   - Only adapt gender where the text actually refers to the person, not for generic parts.

5. General constraints:
   - Do not add any new meaning, do not omit important information.
   - Keep roughly the same level of formality as the English source.
   - Avoid making the text significantly longer than the source.

RESPONSE FORMAT
- Do NOT add explanations or comments.
- Answer strictly as valid JSON with this structure:
{{
  "translations": [
    {{ "key": "KEY_FROM_INPUT", "text": "Translated text here" }},
    {{ "key": "ANOTHER_KEY", "text": "Another translation" }}
  ]
}}
- Return exactly as many translations as segments provided in INPUT.
"""
    
    def build_user_content(self, batch: List[Segment]) -> str:
        """Build the user message payload for API."""
        payload = {"segments": []}
        
        for seg in batch:
            protected, _ = PlaceholderManager.protect(seg.source_text)
            payload["segments"].append({
                "key": seg.key,
                "sheet": seg.sheet,
                "source": protected,
                "comment": seg.comment,
            })
        
        return json.dumps(payload, ensure_ascii=False)
    
    def translate_batch(self, batch: List[Segment]) -> Dict[str, str]:
        """
        Translate a batch of segments.
        
        Returns:
            Dict mapping key -> translated_text
        """
        if self.config.api.use_gemini:
            return self._translate_with_gemini(batch)
        else:
            return self._translate_with_openai(batch)
    
    def _translate_with_gemini(self, batch: List[Segment]) -> Dict[str, str]:
        """Translate using Google Gemini API."""
        system_prompt = self.build_system_prompt()
        user_content = self.build_user_content(batch)
        full_prompt = system_prompt + "\n\n" + user_content
        
        gen_config = types.GenerateContentConfig(
            temperature=0.0,
            candidate_count=1,
            response_mime_type="application/json",
        )
        
        last_exception = None
        
        for attempt in range(1, self.config.api.max_retries_gemini + 1):
            try:
                logger.debug(
                    f"[Gemini] Calling {self.config.api.gemini_model} for batch of "
                    f"{len(batch)} segments (attempt {attempt}/{self.config.api.max_retries_gemini})"
                )
                
                response = self.client.models.generate_content(
                    model=self.config.api.gemini_model,
                    contents=full_prompt,
                    config=gen_config,
                )
                
                raw_text = response.text
                result = self._parse_json_response(raw_text)
                
                if result:
                    logger.debug(f"[Gemini] Successfully translated {len(result)} segments")
                
                return result
            
            except json.JSONDecodeError as e:
                logger.error(f"[Gemini] JSON parse error: {e}")
                last_exception = e
            
            except Exception as e:
                msg = str(e)
                
                # Handle rate limiting
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "rate limit" in msg.lower():
                    wait_time = self.config.api.rate_limit_wait * attempt
                    logger.warning(f"[Gemini] Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                
                logger.error(f"[Gemini] API error (attempt {attempt}): {e}")
                last_exception = e
                
                if attempt < self.config.api.max_retries_gemini:
                    wait_time = 5.0 * attempt
                    logger.debug(f"[Gemini] Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        if last_exception:
            raise last_exception
        raise RuntimeError("Failed to translate batch with Gemini")
    
    def _translate_with_openai(self, batch: List[Segment]) -> Dict[str, str]:
        """Translate using OpenAI API."""
        system_prompt = self.build_system_prompt()
        user_content = self.build_user_content(batch)
        
        last_exception = None
        
        for attempt in range(1, self.config.api.max_retries_openai + 1):
            try:
                logger.debug(
                    f"[OpenAI] Calling {self.config.api.openai_model} for batch of "
                    f"{len(batch)} segments (attempt {attempt}/{self.config.api.max_retries_openai})"
                )
                
                response = self.client.responses.create(
                    model=self.config.api.openai_model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ]
                )
                
                raw_text = response.output[0].content[0].text
                result = self._parse_json_response(raw_text)
                
                if result:
                    logger.debug(f"[OpenAI] Successfully translated {len(result)} segments")
                
                return result
            
            except json.JSONDecodeError as e:
                logger.error(f"[OpenAI] JSON parse error: {e}")
                last_exception = e
            
            except Exception as e:
                msg = str(e)
                
                # Handle rate limiting
                if "rate_limit_exceeded" in msg or "Rate limit reached" in msg:
                    wait_time = self.config.api.rate_limit_wait * attempt
                    logger.warning(f"[OpenAI] Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                
                logger.error(f"[OpenAI] API error (attempt {attempt}): {e}")
                last_exception = e
                
                if attempt < self.config.api.max_retries_openai:
                    wait_time = 5.0 * attempt
                    logger.debug(f"[OpenAI] Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        if last_exception:
            raise last_exception
        raise RuntimeError("Failed to translate batch with OpenAI")
    
    @staticmethod
    def _parse_json_response(raw_text: str) -> Dict[str, str]:
        """Parse JSON response from API."""
        data = json.loads(raw_text)
        
        if "translations" not in data:
            raise ValueError("Missing 'translations' key in API response")
        
        if not isinstance(data["translations"], list):
            raise ValueError("'translations' must be a list")
        
        result = {}
        for item in data["translations"]:
            if isinstance(item, dict):
                key = item.get("key")
                text = item.get("text", "")
                if key:
                    result[str(key)] = str(text)
        
        return result
