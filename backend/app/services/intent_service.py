from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from .base import ModelService


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class IntentResult:
    action: str
    target_object: str
    replacement_object: str
    attributes: dict[str, str]


class IntentService(ModelService):
    model_name = "Qwen2.5-3B-Instruct GGUF"

    def predict(self, instruction: str) -> IntentResult:
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

        result = IntentResult(
            action=action,
            target_object=target,
            replacement_object=replacement,
            attributes=attributes,
        )
        logger.info("Intent parsed: %s", result)
        return result

