from __future__ import annotations

import gc
import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.config import settings
from .base import ModelService


logger = logging.getLogger(__name__)

_ALLOWED_ACTIONS = {
    "remove",
    "replace",
    "add",
    "change_color",
    "enhance",
    "blur",
    "clean",
    "restore",
    "erase_text",
}

_INTENT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "action": {"type": "string", "enum": sorted(_ALLOWED_ACTIONS)},
        "target_object": {"type": "string"},
        "replacement_object": {"type": "string"},
        "attributes": {
            "type": "object",
            "additionalProperties": {"type": "string"},
            "properties": {
                "color": {"type": "string"},
                "style": {"type": "string"},
            },
        },
    },
    "required": ["action", "target_object", "replacement_object", "attributes"],
}


@dataclass(slots=True)
class IntentResult:
    action: str
    target_object: str
    replacement_object: str
    attributes: dict[str, str]


class IntentService(ModelService):
    model_name = "Qwen2.5-3B-Instruct GGUF"

    def __init__(self) -> None:
        self.model = None
        self.grammar = None
        self.model_path = Path(settings.intent_model_path)
        self.n_ctx = settings.intent_model_n_ctx
        self.n_threads = settings.intent_model_n_threads
        self.n_gpu_layers = settings.intent_model_n_gpu_layers
        self.max_tokens = settings.intent_model_max_tokens
        self.temperature = settings.intent_model_temperature
        self.top_p = settings.intent_model_top_p

    def load_model(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Intent model not found at {self.model_path}. Place the Qwen2.5 GGUF file there or update INTENT_MODEL_PATH."
            )

        try:
            from llama_cpp import Llama
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "llama-cpp-python is required for the intent stage. Install project dependencies first."
            ) from exc

        try:
            from llama_cpp import LlamaGrammar
        except ImportError:
            LlamaGrammar = None  # type: ignore[assignment]

        threads = self.n_threads or max(1, min(4, os.cpu_count() or 4))
        self.model = Llama(
            model_path=str(self.model_path),
            n_ctx=self.n_ctx,
            n_threads=threads,
            n_gpu_layers=self.n_gpu_layers,
            verbose=False,
        )

        if LlamaGrammar is not None:
            try:
                self.grammar = LlamaGrammar.from_json_schema(json.dumps(_INTENT_JSON_SCHEMA))
            except Exception:  # noqa: BLE001
                self.grammar = None
        else:
            self.grammar = None

        logger.info("Model loaded: %s (%s)", self.model_name, self.model_path)

    def cleanup(self) -> None:
        self.grammar = None
        if self.model is not None:
            try:
                self.model.close()
            except Exception:  # noqa: BLE001
                pass
        self.model = None
        gc.collect()
        logger.info("Cleanup complete: %s", self.model_name)

    def unload_model(self) -> None:
        self.model = None
        self.grammar = None
        gc.collect()
        logger.info("Model unloaded: %s", self.model_name)

    def predict(self, instruction: str) -> IntentResult:
        text = instruction.strip()
        if not text:
            raise ValueError("Instruction cannot be empty")

        if self.model is None:
            self.load_model()

        payload = self._generate_json(self._build_prompt(text))
        result = self._normalize_payload(payload, text)
        logger.info("Intent parsed: %s", result)
        return result

    def _build_prompt(self, instruction: str) -> str:
        schema = json.dumps(_INTENT_JSON_SCHEMA, ensure_ascii=False, indent=2)
        return (
            "You are an image-editing intent parser. "
            "Extract the user's request into valid JSON only. "
            "Return exactly one JSON object that matches this schema:\n"
            f"{schema}\n\n"
            "Rules:\n"
            "- Use one of these actions: remove, replace, add, change_color, enhance, blur, clean, restore, erase_text.\n"
            "- target_object should be the object or region to edit.\n"
            "- replacement_object should be empty unless replacement is explicitly requested.\n"
            "- attributes may include color or style when relevant.\n"
            "- Do not include markdown, commentary, or code fences.\n\n"
            f'Instruction: "{instruction}"\n'
            "JSON:"
        )

    def _generate_json(self, prompt: str) -> dict[str, Any]:
        assert self.model is not None
        generation_kwargs = {
            "prompt": prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stop": ["\n\n", "```"],
        }
        if self.grammar is not None:
            generation_kwargs["grammar"] = self.grammar

        try:
            response = self.model.create_completion(**generation_kwargs)
        except TypeError:
            generation_kwargs.pop("grammar", None)
            response = self.model.create_completion(**generation_kwargs)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Intent model inference failed: {exc}") from exc

        raw_text = response["choices"][0]["text"]
        return self._parse_json_response(raw_text)

    def _parse_json_response(self, raw_text: str) -> dict[str, Any]:
        cleaned = raw_text.strip()
        cleaned = cleaned.removeprefix("```json").removesuffix("```").strip()
        if not cleaned.startswith("{"):
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if match:
                cleaned = match.group(0)
        try:
            parsed = json.loads(cleaned)
            if not isinstance(parsed, dict):
                raise ValueError("model did not return an object")
            return parsed
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Unable to parse intent JSON from model output: {raw_text!r}") from exc

    def _normalize_payload(self, payload: dict[str, Any], instruction: str) -> IntentResult:
        action = str(payload.get("action", "clean")).strip().lower() or "clean"
        if action not in _ALLOWED_ACTIONS:
            action = "clean"

        target_object = str(payload.get("target_object", "")).strip()
        replacement_object = str(payload.get("replacement_object", "")).strip()
        attributes_raw = payload.get("attributes") or {}
        attributes: dict[str, str] = {}
        if isinstance(attributes_raw, dict):
            for key, value in attributes_raw.items():
                key_text = str(key).strip()
                value_text = str(value).strip()
                if key_text and value_text:
                    attributes[key_text] = value_text

        if not target_object:
            fallback = self._fallback_parse(instruction)
            target_object = fallback.target_object
            replacement_object = replacement_object or fallback.replacement_object
            if action not in _ALLOWED_ACTIONS:
                action = fallback.action
            attributes = {**fallback.attributes, **attributes}

        if action == "change_color" and "color" not in attributes and replacement_object:
            attributes["color"] = replacement_object
        if action == "erase_text":
            target_object = target_object or "text"

        return IntentResult(
            action=action,
            target_object=target_object or instruction,
            replacement_object=replacement_object,
            attributes=attributes,
        )

    def _fallback_parse(self, instruction: str) -> IntentResult:
        text = instruction.strip()
        lower = text.lower()
        action = "clean"
        target = ""
        replacement = ""
        attributes: dict[str, str] = {}

        action_patterns = {
            "remove": r"remove (?:the )?(.*)",
            "replace": r"replace (?:the )?(.*?) with (?:a |an )?(.*)",
            "add": r"add (?:a |an |the )?(.*)",
            "change_color": r"change (?:the )?(.*?) color to (.*)",
            "erase_text": r"(?:remove|erase) text",
            "blur": r"blur (?:the )?(.*)",
            "restore": r"restore (?:the )?(.*)",
            "enhance": r"enhance (?:the )?(.*)",
        }

        for candidate, pattern in action_patterns.items():
            match = re.search(pattern, lower)
            if match:
                action = candidate
                groups = [g.strip(" .") for g in match.groups() if g]
                if candidate == "replace" and len(groups) >= 2:
                    target, replacement = groups[0], groups[1]
                elif candidate == "change_color" and len(groups) >= 2:
                    target, replacement = groups[0], groups[1]
                    attributes["color"] = replacement
                    replacement = ""
                elif groups:
                    target = groups[0]
                break

        if not target:
            if "text" in lower:
                action = "erase_text"
                target = "text"
            else:
                target = text

        if "blue" in lower:
            attributes.setdefault("color", "blue")
        if "gold" in lower:
            attributes.setdefault("style", "gold")

        return IntentResult(
            action=action,
            target_object=target,
            replacement_object=replacement,
            attributes=attributes,
        )
