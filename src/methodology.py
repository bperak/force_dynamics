import json
import random
from typing import Dict, Tuple

from .llm.openai_client import chat_complete as openai_chat
from .llm.gemini_client import chat_complete as gemini_chat

FD_FRAMEWORK = """
Force Dynamics (Talmy, 2000) Framework:

CORE CONCEPTS:
- Agonist: The entity whose situation is being described (typically the subject)
- Antagonist: The opposing force entity (may be explicit or implicit)
- Force Relations: How Agonist and Antagonist interact

FORCE RELATION TYPES:
1. Causation: Antagonist causes Agonist to act/change state
2. Permission/Letting: Antagonist allows Agonist to act
3. Blocking/Prevention: Antagonist prevents Agonist from acting
4. Overcoming: Agonist overcomes opposing force
"""


def _call_model(provider: str, model: str, system_prompt: str, user_prompt: str) -> str:
    if provider == "openai":
        return openai_chat(model, system_prompt, user_prompt, temperature=0.0)
    if provider == "gemini":
        return gemini_chat(model, system_prompt, user_prompt, temperature=0.0)
    raise ValueError(f"Unknown provider: {provider}")


def get_translation(provider: str, model: str, system_prompt: str, user_prompt: str) -> str:
    return _call_model(provider, model, system_prompt, user_prompt)


def parse_json_response(text: str) -> Dict:
    cleaned = text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: try to locate JSON object
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            return json.loads(cleaned[start : end + 1])
        return {"error": "json_parse_failed", "raw": text}


def blind_evaluate(
    provider: str,
    model: str,
    system_prompt: str,
    original_text: str,
    translation_a: str,
    translation_b: str,
    translation_c: str,
) -> Dict:
    user_prompt = f"""Evaluate three translations of the same English sentence, focusing EXCLUSIVELY on the verb phrase and its preservation of Force Dynamics relations.

{FD_FRAMEWORK}

EVALUATION CRITERIA:

1. Lexis (verb phrase only):
   - Word choice appropriateness
   - Idiomaticity in target language
   - Register appropriateness

2. Syntax (verb phrase only):
   - Grammatical accuracy
   - Structural correctness
   - Word order appropriateness

3. Semantics (verb phrase only):
   - Meaning preservation
   - Force Dynamics relations:
     * Identify Agonist and Antagonist (if present)
     * Identify force relation type (causation, permission, blocking, etc.)
     * Assess preservation of FD structure from source

Original sentence (English): {original_text}

Translation A: {translation_a}
Translation B: {translation_b}
Translation C: {translation_c}

For each translation (A, B, C):
1. Describe the verb phrase in terms of lexis, syntax, semantics (including FD analysis)
2. Provide a numerical score (0.0 to 1.0) for verb phrase quality

Output format (JSON only, no other text):
{{
  "translation_A_description": "string",
  "translation_A_score": float,
  "translation_B_description": "string",
  "translation_B_score": float,
  "translation_C_description": "string",
  "translation_C_score": float,
  "comparison": "string"
}}
"""

    response = _call_model(provider, model, system_prompt, user_prompt)
    return parse_json_response(response)


def prepare_blind_labels(rng: random.Random, gpt: str, google: str, human: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    entries = [("GPT", gpt), ("Google", google), ("Human", human)]
    rng.shuffle(entries)
    labels = {"A": entries[0][1], "B": entries[1][1], "C": entries[2][1]}
    mapping = {"A": entries[0][0], "B": entries[1][0], "C": entries[2][0]}
    return labels, mapping
