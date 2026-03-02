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


SMART_INPUT_SYSTEM_PROMPT = """You are an expert academic writing assistant. Given a brief, informal description of a diagram the user wants to create, you must produce two outputs:

1. **METHOD_SECTION**: A detailed methodology section (in Markdown) describing the system, pipeline, or architecture. Write it as if it were part of an academic paper. Include component names, data flow, and relationships. Use subsections (###) for major components.

2. **CAPTION**: A single-sentence figure caption starting with "Figure 1:" that summarizes what the diagram shows.

Format your response EXACTLY as follows (use these exact delimiters):
===METHOD_SECTION===
(your method section here)
===CAPTION===
(your caption here)
===END===
"""

SMART_INPUT_SYSTEM_PROMPT_KO = """You are an expert academic writing assistant. Given a brief, informal description of a diagram the user wants to create, you must produce two outputs IN KOREAN (한국어):

1. **METHOD_SECTION**: A detailed methodology section (in Markdown) describing the system, pipeline, or architecture. Write it as if it were part of an academic paper. Include component names, data flow, and relationships. Use subsections (###) for major components. Write entirely in Korean except for technical terms and mathematical notation.

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

    # Use lightweight model for Smart Input (cheaper, higher quota)
    lite_model = generation_utils.get_config_val("defaults", "lite_model_name", "LITE_MODEL_NAME", "")
    if not lite_model:
        lite_model = generation_utils.get_config_val("defaults", "model_name", "MODEL_NAME", "")

    response_list = await generation_utils.call_gemini_with_retry_async(
        model_name=lite_model,
        contents=content_list,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            candidate_count=1,
            max_output_tokens=8192,
        ),
        max_attempts=5,
        retry_delay=10,
    )

    raw = response_list[0] if response_list else ""
    if raw == "Error" or not raw.strip():
        raise RuntimeError("API call failed after all retries. The model may be temporarily unavailable.")
    return _parse_smart_input_response(raw)


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
