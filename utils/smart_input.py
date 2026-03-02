# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Smart Input: Converts a brief user description into a structured
method section and figure caption suitable for PaperVizAgent.
"""

import re
from utils import generation_utils
from google.genai import types


SMART_INPUT_SYSTEM_PROMPT = """You are an expert technical writing assistant. Given a brief, informal description of a diagram the user wants to create, you must produce two outputs:

1. **METHOD_SECTION**: A detailed description (in Markdown) of the system, pipeline, architecture, or concept being illustrated. Include component names, data flow, and relationships. Use subsections (###) for major components. Write clearly and precisely as if explaining for a technical document or academic paper.

2. **CAPTION**: A single-sentence figure caption starting with "Figure 1:" that summarizes what the diagram shows.

Format your response EXACTLY as follows (use these exact delimiters):
===METHOD_SECTION===
(your method section here)
===CAPTION===
(your caption here)
===END===
"""

SMART_INPUT_SYSTEM_PROMPT_KO = """You are an expert technical writing assistant. Given a brief, informal description of a diagram the user wants to create, you must produce two outputs IN KOREAN (한국어):

1. **METHOD_SECTION**: A detailed description (in Markdown) of the system, pipeline, architecture, or concept being illustrated. Include component names, data flow, and relationships. Use subsections (###) for major components. Write entirely in Korean except for technical terms and mathematical notation.

2. **CAPTION**: A single-sentence figure caption starting with "Figure 1:" that summarizes what the diagram shows, written in Korean.

Format your response EXACTLY as follows (use these exact delimiters):
===METHOD_SECTION===
(your method section here in Korean)
===CAPTION===
(your caption here in Korean)
===END===
"""


async def generate_smart_input(brief_description: str, language: str = "en") -> dict:
    """Convert a brief description into a structured method section + caption.

    Args:
        brief_description: A short, informal description of the desired diagram.
        language: "en" for English output, "ko" for Korean output.

    Returns:
        dict with keys "method" and "caption".
    """
    system_prompt = SMART_INPUT_SYSTEM_PROMPT_KO if language == "ko" else SMART_INPUT_SYSTEM_PROMPT

    user_prompt = f"Create a detailed method section and figure caption for the following diagram idea:\n\n{brief_description}"

    content_list = [{"type": "text", "text": user_prompt}]

    gen_config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
        candidate_count=1,
        max_output_tokens=8192,
    )

    # Build ordered list of models to try: lite first, then main as fallback
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
                return _parse_smart_input_response(raw)
        except Exception as e:
            last_error = e
            print(f"[Smart Input] Model '{model_name}' failed: {e}. Trying next model...")
            continue

    raise RuntimeError(
        f"All models failed for Smart Input. Last error: {last_error}"
    )


def _parse_smart_input_response(raw: str) -> dict:
    """Parse the delimited response into method and caption."""
    method = ""
    caption = ""

    method_match = re.search(r"===METHOD_SECTION===(.*?)===CAPTION===", raw, re.DOTALL)
    caption_match = re.search(r"===CAPTION===(.*?)===END===", raw, re.DOTALL)

    if method_match:
        method = method_match.group(1).strip()
    if caption_match:
        caption = caption_match.group(1).strip()

    # Fallback: if delimiters not found, use the whole response as method
    if not method and not caption:
        method = raw.strip()
        caption = "Figure 1: Overview of the proposed system."

    return {"method": method, "caption": caption}
