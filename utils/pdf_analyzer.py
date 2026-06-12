"""
PDF Analyzer: Analyzes academic paper PDFs and suggests diagram candidates.
"""

import re
import json
from utils import generation_utils
from google.genai import types

try:
    import json_repair
except ImportError:
    json_repair = None


PDF_ANALYSIS_SYSTEM_PROMPT = """You are an expert scientific diagram analyst. Given a research paper PDF, analyze the methodology, architecture, and key concepts, then suggest 3-7 diagrams that would effectively illustrate the paper's contributions.

For each suggestion, provide:
- title: A short, descriptive title for the diagram
- description: A 1-2 sentence description of what the diagram should show, written as a diagram creation prompt
- section: Which section of the paper this relates to (e.g., "Method", "Architecture", "Training Pipeline")

Format your response EXACTLY as follows (use these exact delimiters):
===SUGGESTIONS===
[
  {"title": "...", "description": "...", "section": "..."},
  ...
]
===END===
"""

PDF_ANALYSIS_SYSTEM_PROMPT_KO = """You are an expert scientific diagram analyst. Given a research paper PDF, analyze the methodology, architecture, and key concepts, then suggest 3-7 diagrams that would effectively illustrate the paper's contributions. Write ALL output in Korean (한국어), except for technical terms.

For each suggestion, provide:
- title: A short, descriptive title for the diagram (in Korean)
- description: A 1-2 sentence description of what the diagram should show, written as a diagram creation prompt (in Korean)
- section: Which section of the paper this relates to (in Korean, e.g., "방법론", "아키텍처", "학습 파이프라인")

Format your response EXACTLY as follows (use these exact delimiters):
===SUGGESTIONS===
[
  {"title": "...", "description": "...", "section": "..."},
  ...
]
===END===
"""


async def analyze_pdf_for_diagrams(pdf_bytes: bytes, language: str = "ko") -> list[dict]:
    """Analyze a PDF paper and return diagram suggestions.

    Args:
        pdf_bytes: Raw bytes of the PDF file.
        language: "en" or "ko" for output language.

    Returns:
        List of dicts with keys: title, description, section.
    """
    system_prompt = PDF_ANALYSIS_SYSTEM_PROMPT_KO if language == "ko" else PDF_ANALYSIS_SYSTEM_PROMPT

    content_list = [
        {"type": "text", "text": "Analyze this research paper and suggest diagrams that would best illustrate its key contributions and methodology."},
        {"type": "pdf", "data": pdf_bytes, "mime_type": "application/pdf"},
    ]

    gen_config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
        candidate_count=1,
        max_output_tokens=8192,
    )

    lite_model = generation_utils.get_config_val("defaults", "lite_model_name", "LITE_MODEL_NAME", "")
    main_model = generation_utils.get_config_val("defaults", "model_name", "MODEL_NAME", "")
    models_to_try = [m for m in [lite_model, main_model] if m]

    if not models_to_try:
        raise RuntimeError("No model configured. Set lite_model_name or model_name in configs/model_config.yaml.")

    last_error = None
    for model_name in models_to_try:
        try:
            response_list = await generation_utils.call_gemini_with_retry_async(
                model_name=model_name,
                contents=content_list,
                config=gen_config,
                max_attempts=3,
                retry_delay=5,
            )
            raw = response_list[0] if response_list else ""
            if raw and raw != "Error" and raw.strip():
                return _parse_suggestions(raw)
            last_error = RuntimeError(f"Model '{model_name}' returned empty or error response")
            print(f"[PDF Analyzer] {last_error}. Trying next model...")
        except Exception as e:
            last_error = e
            print(f"[PDF Analyzer] Model '{model_name}' failed: {e}. Trying next model...")
            continue

    raise RuntimeError(f"All models failed for PDF analysis. Last error: {last_error}")


def _parse_suggestions(raw: str) -> list[dict]:
    """Parse the delimited response into a list of suggestion dicts."""
    match = re.search(r"===SUGGESTIONS===(.*?)===END===", raw, re.DOTALL)
    json_str = match.group(1).strip() if match else raw.strip()

    try:
        suggestions = json.loads(json_str)
    except json.JSONDecodeError:
        if json_repair is not None:
            suggestions = json_repair.loads(json_str)
        else:
            raise

    if not isinstance(suggestions, list):
        suggestions = [suggestions]

    valid = []
    for s in suggestions:
        if isinstance(s, dict) and "title" in s and "description" in s:
            valid.append({
                "title": s["title"],
                "description": s["description"],
                "section": s.get("section", ""),
            })
    return valid
