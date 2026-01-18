import os
import google.generativeai as genai


def chat_complete(model: str, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
    if "GEMINI_API_KEY" not in os.environ:
        raise RuntimeError("GEMINI_API_KEY is not set")

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model_obj = genai.GenerativeModel(model)

    # Gemini does not have a strict system/user separation in the same way.
    # We concatenate system + user prompts for determinism.
    content = f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}"
    resp = model_obj.generate_content(
        content,
        generation_config={"temperature": temperature},
    )
    return resp.text.strip()
