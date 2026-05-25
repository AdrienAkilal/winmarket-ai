import json
import time
from typing import Optional
from src.core.config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    LLM_MAX_TOKENS,
    LLM_TIMEOUT_SECONDS,
    LLM_TEMPERATURE,
    LLM_TOP_P,
)
from src.core.logger import get_agent_logger
from src.core.error_handler import retry_with_backoff, DEFAULT_RETRY_CONFIG

logger = get_agent_logger("llm_client")

_RETRY_SUFFIX = (
    "\n\nATTENTION : Ta réponse précédente n'était pas un JSON valide. "
    "Réponds UNIQUEMENT avec un objet JSON bien formé, sans texte avant ni après, "
    "sans balises markdown, sans commentaires."
)


class ClaudeClient:
    def __init__(self):
        import os
        # Read key at instantiation time (not from cached config constant) so
        # it picks up the key even if .env was added after the process started.
        api_key = os.getenv("ANTHROPIC_API_KEY", "") or ANTHROPIC_API_KEY
        self.enabled = bool(api_key and not api_key.startswith("sk-ant-xxxx"))
        self.client = None
        self.model = ANTHROPIC_MODEL

        if self.enabled:
            try:
                import anthropic
                import httpx
                self.client = anthropic.Anthropic(
                    api_key=api_key,
                    timeout=httpx.Timeout(
                        connect=10.0,
                        read=float(LLM_TIMEOUT_SECONDS),
                        write=10.0,
                        pool=5.0,
                    ),
                )
                logger.info(f"Claude API client initialized — model={self.model}")
            except Exception as e:
                self.enabled = False
                logger.error(f"Failed to initialize Claude client: {e}")
        else:
            logger.warning("Claude client disabled (no API key or invalid format)")

    @retry_with_backoff(config=DEFAULT_RETRY_CONFIG)
    def complete(
        self,
        prompt: str,
        system: str = None,
        temperature: float = None,
        max_tokens: Optional[int] = None,
    ) -> Optional[str]:
        """
        Call Claude API for text completion with automatic retry.

        Args:
            prompt: User message for Claude
            system: Optional system prompt (sets Claude's role and behavior)
            temperature: Sampling temperature (overrides config default)
            max_tokens: Maximum tokens in response (default from config)

        Returns:
            Generated text or None if failed
        """
        if not self.enabled or self.client is None:
            logger.warning("Claude client not available, skipping completion")
            return None

        if max_tokens is None:
            max_tokens = LLM_MAX_TOKENS
        if temperature is None:
            temperature = LLM_TEMPERATURE

        start_time = time.time()

        try:
            kwargs = dict(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            if system:
                kwargs["system"] = system

            msg = self.client.messages.create(**kwargs)

            result = "\n".join([b.text for b in msg.content if hasattr(b, "text")])
            duration_ms = (time.time() - start_time) * 1000

            duration_ms = (time.time() - start_time) * 1000
            logger.debug(f"Claude completion OK — {len(result)} chars in {duration_ms:.0f}ms")
            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Claude completion failed ({type(e).__name__}): {e} [{duration_ms:.0f}ms]")
            raise

    def json_complete(
        self,
        prompt: str,
        system: str = None,
        temperature: float = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
    ) -> Optional[dict]:
        """
        Call Claude API and parse JSON response, with JSON-specific retry logic.

        Args:
            prompt: User message requesting JSON output
            system: Optional system prompt
            temperature: Sampling temperature (overrides config default)
            max_tokens: Maximum tokens in response
            max_retries: Number of JSON parse retry attempts

        Returns:
            Parsed JSON dict or None if parsing failed after all retries
        """
        current_prompt = prompt
        for attempt in range(max_retries):
            text = self.complete(current_prompt, system=system, temperature=temperature, max_tokens=max_tokens)
            if not text:
                return None
            result = self._parse_json_response(text)
            if result is not None:
                return result
            logger.warning(f"JSON parse failed, retrying (attempt {attempt + 1}/{max_retries})")
            current_prompt = prompt + _RETRY_SUFFIX
            if attempt < max_retries - 1:
                time.sleep(1)
        return None

    @staticmethod
    def _parse_json_response(text: str) -> Optional[dict]:
        """
        Parse JSON from Claude response (handles markdown code blocks, etc).
        
        Args:
            text: Raw response text from Claude
        
        Returns:
            Parsed dict or None
        """
        text = text.strip()
        
        # Remove markdown code fences if present
        if "```" in text:
            start = text.find("```")
            end = text.rfind("```")
            if start != end:
                inner = text[start+3:end].strip()
                if inner.startswith("json"):
                    inner = inner[4:].strip()
                text = inner
        
        # Extract JSON object (first { to last })
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end >= 0:
            text = text[start:end+1]
        
        try:
            result = json.loads(text)
            logger.debug(f"JSON parsing successful ({len(str(result))} chars)")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e} | preview: {text[:200]}")
            return None
