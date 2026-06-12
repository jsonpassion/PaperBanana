# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Parallel Streamlit Demo for PaperVizAgent
Accepts user text input, duplicates it 10 times, and runs parallel processing
to generate multiple diagram candidates for comparison.
"""

import streamlit as st
import asyncio
import base64
import json
from io import BytesIO
from PIL import Image
from pathlib import Path
import sys
import os
from datetime import datetime

from translations import TRANSLATIONS
from example_templates import EXAMPLE_TEMPLATES, EXAMPLE_DISPLAY_NAMES_KO


def run_async(coro):
    """Run async coroutine in a fresh event loop (Streamlit-safe).

    run_async() closes the loop after finishing, which orphans the
    Gemini client's async session.  Creating a brand-new loop each time
    avoids the 'Event loop is closed' error on successive calls.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("DEBUG: Importing agents...")
try:
    from agents.planner_agent import PlannerAgent
    print("DEBUG: Imported PlannerAgent")
    from agents.visualizer_agent import VisualizerAgent
    from agents.stylist_agent import StylistAgent
    from agents.critic_agent import CriticAgent
    from agents.retriever_agent import RetrieverAgent
    from agents.vanilla_agent import VanillaAgent
    from agents.polish_agent import PolishAgent
    print("DEBUG: Imported all agents")
    from utils import config
    from utils.paperviz_processor import PaperVizProcessor
    print("DEBUG: Imported utils")

    import yaml
    config_path = Path(__file__).parent / "configs" / "model_config.yaml"
    model_config_data = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            model_config_data = yaml.safe_load(f) or {}

    def get_config_val(section, key, env_var, default=""):
        val = os.getenv(env_var)
        if not val and section in model_config_data:
            val = model_config_data[section].get(key)
        return val or default

except ImportError as e:
    print(f"DEBUG: ImportError: {e}")
    import traceback
    traceback.print_exc()
    raise e
except Exception as e:
    print(f"DEBUG: Exception during import: {e}")
    import traceback
    traceback.print_exc()
    raise e

SUPPORTED_LANGUAGES = {"English": "en", "한국어": "ko"}

# ── Constants ──
ANALYSIS_TEMPERATURE = 0.2
ANALYSIS_MAX_TOKENS = 2048
IMAGE_GEN_TEMPERATURE = 1.0
IMAGE_GEN_MAX_TOKENS = 8192
MAX_CONCURRENT = 10
DEFAULT_NUM_COPIES = 10
MAX_CRITIC_ROUNDS_CHECK = 4
RESULTS_GRID_COLS = 3
ASPECT_RATIOS = ["16:9", "21:9", "3:2"]
RESOLUTIONS = ["2K", "4K"]

def t(key, **kwargs):
    """Return the translated string for the current language."""
    lang = st.session_state.get("language", "ko")
    text = TRANSLATIONS.get(lang, TRANSLATIONS["ko"]).get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

st.set_page_config(
    layout="wide",
    page_title="PaperVizAgent Parallel Demo",
    page_icon="🍌"
)

# Custom CSS for bigger tabs and cleaner UI
st.markdown("""
<style>
/* Bigger, bolder tab buttons */
div[data-testid="stTabs"] button[data-baseweb="tab"] {
    font-size: 1.25rem;
    font-weight: 600;
    padding: 0.75rem 1.5rem;
}
/* Active tab highlight */
div[data-testid="stTabs"] button[aria-selected="true"] {
    border-bottom: 3px solid #ff6b35;
}
/* Tab list bottom border */
div[data-testid="stTabs"] [role="tablist"] {
    gap: 0.5rem;
    border-bottom: 2px solid #e0e0e0;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

def clean_text(text):
    """Clean text by removing invalid UTF-8 surrogate characters."""
    if not text:
        return text
    if isinstance(text, str):
        # Remove surrogate characters that cause UnicodeEncodeError
        return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    return text

def base64_to_image(b64_str):
    """Convert base64 string to PIL Image."""
    if not b64_str:
        return None
    try:
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        image_data = base64.b64decode(b64_str)
        return Image.open(BytesIO(image_data))
    except Exception:
        return None

def create_sample_inputs(method_content, caption, diagram_type="Pipeline", aspect_ratio="16:9", num_copies=DEFAULT_NUM_COPIES, max_critic_rounds=3, diagram_language="en"):
    """Create multiple copies of the input data for parallel processing."""
    base_input = {
        "filename": "demo_input",
        "caption": caption,
        "content": method_content,
        "visual_intent": caption,
        "additional_info": {
            "rounded_ratio": aspect_ratio
        },
        "max_critic_rounds": max_critic_rounds,
        "diagram_language": diagram_language,
    }
    
    # Create num_copies identical inputs, each with a unique identifier
    inputs = []
    for i in range(num_copies):
        input_copy = base_input.copy()
        input_copy["filename"] = f"demo_input_candidate_{i}"
        input_copy["candidate_id"] = i
        inputs.append(input_copy)
    
    return inputs

async def process_parallel_candidates(data_list, exp_mode="dev_planner_critic", retrieval_setting="auto", model_name="", progress_callback=None):
    """Process multiple candidates in parallel using PaperVizProcessor."""
    # Create experiment config
    exp_config = config.ExpConfig(
        dataset_name="Demo",
        split_name="demo",
        exp_mode=exp_mode,
        retrieval_setting=retrieval_setting,
        model_name=model_name,
        work_dir=Path(__file__).parent,
    )

    # Initialize processor with all agents
    processor = PaperVizProcessor(
        exp_config=exp_config,
        vanilla_agent=VanillaAgent(exp_config=exp_config),
        planner_agent=PlannerAgent(exp_config=exp_config),
        visualizer_agent=VisualizerAgent(exp_config=exp_config),
        stylist_agent=StylistAgent(exp_config=exp_config),
        critic_agent=CriticAgent(exp_config=exp_config),
        retriever_agent=RetrieverAgent(exp_config=exp_config),
        polish_agent=PolishAgent(exp_config=exp_config),
    )

    # Process all candidates in parallel (concurrency controlled by processor)
    results = []
    concurrent_num = MAX_CONCURRENT

    async for result_data in processor.process_queries_batch(
        data_list, max_concurrent=concurrent_num, do_eval=False,
        progress_callback=progress_callback,
    ):
        results.append(result_data)

    return results

async def _analyze_image_for_corrections(client, image_bytes, edit_prompt, model_name, _report):
    """
    Phase 1: Use a vision-language model to analyze the image and produce
    specific, actionable correction instructions for the image model.
    Works with any type of diagram/image — no domain assumption.
    """
    from google.genai import types

    _report("analyze", model=model_name)

    analysis_prompt = (
        "You are an image quality analyst. Examine this image and list "
        "specific corrections the image editor can realistically apply.\n\n"
        "CHECK:\n"
        "1. DUPLICATE LABELS: Any text appearing more than once where it shouldn't? "
        "Specify which to keep and which to rename.\n"
        "2. NONSENSICAL TEXT: Any garbled, gibberish, or contextually wrong text? "
        "Suggest the correct replacement.\n"
        "3. ARROWS: Any disconnected or illogical connectors?\n"
        "4. OVERLAPS: Any text overflowing boundaries or overlapping other elements?\n\n"
        f"USER'S EDIT REQUEST:\n{edit_prompt}\n\n"
        "OUTPUT: ONLY a numbered list of concrete corrections with locations.\n"
        "If no corrections needed: \"NO CORRECTIONS NEEDED\"\n"
        "Max 8 items. Only list problems the image editor can fix by redrawing text, "
        "labels, or connectors — do NOT request layout restructuring or content generation."
    )

    contents = [
        types.Part.from_text(text=analysis_prompt),
        types.Part.from_bytes(mime_type="image/jpeg", data=image_bytes),
    ]

    config = types.GenerateContentConfig(
        temperature=ANALYSIS_TEMPERATURE,
        max_output_tokens=ANALYSIS_MAX_TOKENS,
    )

    response = await asyncio.to_thread(
        client.models.generate_content,
        model=model_name,
        contents=contents,
        config=config,
    )

    analysis_text = ""
    if response.candidates and response.candidates[0].content.parts:
        analysis_text = response.candidates[0].content.parts[0].text or ""

    # Count corrections
    lines = [l.strip() for l in analysis_text.strip().split("\n") if l.strip()]
    n_corrections = 0 if "NO CORRECTIONS NEEDED" in analysis_text.upper() else len(
        [l for l in lines if l and l[0].isdigit()]
    )
    _report("analyze_done", n=n_corrections, analysis=analysis_text)

    return analysis_text, n_corrections


async def refine_image_with_nanoviz(image_bytes, edit_prompt, aspect_ratio="21:9", image_size="2K", num_rounds=1, progress_callback=None):
    """
    Multi-round two-phase refinement pipeline.
    Each round: Phase 1 (analyze) → Phase 2 (generate).
    Subsequent rounds use the previous round's output as input.

    Returns:
        Tuple of (list_of_round_bytes, success_message).
        Each element in the list is the image bytes from that round.
        Empty list on failure.
    """
    def _report(step, **info):
        if progress_callback:
            progress_callback(step, info)

    try:
        from google import genai
        from google.genai import types

        _report("prepare")

        api_key = get_config_val("api_keys", "google_api_key", "GOOGLE_API_KEY", "")
        if not api_key:
            return [], "Google API Key not configured. Set it in configs/model_config.yaml or GOOGLE_API_KEY env var."

        client = genai.Client(api_key=api_key)
        analysis_model = get_config_val("defaults", "model_name", "MODEL_NAME", "")
        image_model = get_config_val("defaults", "image_model_name", "IMAGE_MODEL_NAME", "")

        baseline = (
            "Refine this diagram. Keep the same layout and structure.\n"
            "- Make ALL text razor-sharp and legible. Fix garbled or nonsensical text.\n"
            "- Fix duplicate labels — each label must be unique and accurate.\n"
            "- Arrows must connect clearly from source to destination.\n"
            "- Text must not overflow its containing box or overlap other elements.\n"
            "- Do NOT add new components. Do NOT add figure captions.\n"
        )

        round_results = []
        current_bytes = image_bytes

        for round_i in range(num_rounds):
            if num_rounds > 1:
                _report("round", current=round_i + 1, total=num_rounds)

            # ── Phase 1: Analyze ──
            analysis_text, n_corrections = await _analyze_image_for_corrections(
                client, current_bytes, edit_prompt, analysis_model, _report
            )

            # ── Phase 2: Generate ──
            if n_corrections > 0:
                full_prompt = (
                    f"{baseline}\n"
                    f"CORRECTIONS (from analysis):\n{analysis_text}\n\n"
                    f"EDIT INSTRUCTIONS:\n{edit_prompt}"
                )
            else:
                full_prompt = f"{baseline}\nEDIT INSTRUCTIONS:\n{edit_prompt}"

            contents = [
                types.Part.from_text(text=full_prompt),
                types.Part.from_bytes(mime_type="image/jpeg", data=current_bytes),
            ]

            gen_config = types.GenerateContentConfig(
                temperature=IMAGE_GEN_TEMPERATURE,
                max_output_tokens=IMAGE_GEN_MAX_TOKENS,
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
            )

            _report("api_call", model=image_model)
            _report("waiting")

            response = await asyncio.to_thread(
                client.models.generate_content,
                model=image_model,
                contents=contents,
                config=gen_config,
            )

            _report("processing")

            # Extract image from response
            result_bytes = None
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        edited_image_data = part.inline_data.data
                        if isinstance(edited_image_data, bytes):
                            result_bytes = edited_image_data
                        elif isinstance(edited_image_data, str):
                            result_bytes = base64.b64decode(edited_image_data)
                        break

            if result_bytes is None:
                return round_results, "No image data found in response"

            round_results.append(result_bytes)
            current_bytes = result_bytes

        return round_results, "✅ Image refined successfully!"

    except Exception as e:
        return [], f"Error: {str(e)}"


def get_evolution_stages(result, exp_mode):
    """Extract all evolution stages (images and descriptions) from the result."""
    task_name = "diagram"
    stages = []
    
    # Stage 1: Planner output
    planner_img_key = f"target_{task_name}_desc0_base64_jpg"
    planner_desc_key = f"target_{task_name}_desc0"
    if planner_img_key in result and result[planner_img_key]:
        stages.append({
            "name": t("stage_planner"),
            "image_key": planner_img_key,
            "desc_key": planner_desc_key,
            "description": t("stage_planner_desc")
        })
    
    # Stage 2: Stylist output (only for demo_full)
    if exp_mode == "demo_full":
        stylist_img_key = f"target_{task_name}_stylist_desc0_base64_jpg"
        stylist_desc_key = f"target_{task_name}_stylist_desc0"
        if stylist_img_key in result and result[stylist_img_key]:
            stages.append({
                "name": t("stage_stylist"),
                "image_key": stylist_img_key,
                "desc_key": stylist_desc_key,
                "description": t("stage_stylist_desc")
            })
    
    # Stage 3+: Critic iterations
    for round_idx in range(MAX_CRITIC_ROUNDS_CHECK):
        critic_img_key = f"target_{task_name}_critic_desc{round_idx}_base64_jpg"
        critic_desc_key = f"target_{task_name}_critic_desc{round_idx}"
        critic_sugg_key = f"target_{task_name}_critic_suggestions{round_idx}"
        
        if critic_img_key in result and result[critic_img_key]:
            stages.append({
                "name": t("stage_critic_round", n=round_idx),
                "image_key": critic_img_key,
                "desc_key": critic_desc_key,
                "suggestions_key": critic_sugg_key,
                "description": t("stage_critic_round_desc", n=round_idx)
            })
    
    return stages

def display_candidate_result(result, candidate_id, exp_mode):
    """Display a single candidate result."""
    task_name = "diagram"
    
    # Determine which image to show based on exp_mode
    # For demo modes, always try to find the last critic round
    final_image_key = None
    final_desc_key = None
    
    # Try to find the last critic round
    for round_idx in range(MAX_CRITIC_ROUNDS_CHECK - 1, -1, -1):
        image_key = f"target_{task_name}_critic_desc{round_idx}_base64_jpg"
        if image_key in result and result[image_key]:
            final_image_key = image_key
            final_desc_key = f"target_{task_name}_critic_desc{round_idx}"
            break
    
    # Fallback if no critic rounds completed
    if not final_image_key:
        if exp_mode == "demo_full":
            # demo_full uses stylist before visualizer
            final_image_key = f"target_{task_name}_stylist_desc0_base64_jpg"
            final_desc_key = f"target_{task_name}_stylist_desc0"
        else:
            # demo_planner_critic uses planner output
            final_image_key = f"target_{task_name}_desc0_base64_jpg"
            final_desc_key = f"target_{task_name}_desc0"
    
    # Display the final image
    if final_image_key and final_image_key in result:
        img = base64_to_image(result[final_image_key])
        if img:
            st.image(img, width="stretch", caption=t("candidate_caption", id=candidate_id))

            # Add download button
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            st.download_button(
                label=t("download_candidate"),
                data=buffered.getvalue(),
                file_name=f"candidate_{candidate_id}.png",
                mime="image/png",
                key=f"download_candidate_{candidate_id}",
                width="stretch"
            )

            # Add refine button (send to Tab 2)
            if st.button(
                t("refine_from_candidate_button"),
                key=f"refine_candidate_{candidate_id}",
                width="stretch"
            ):
                st.session_state["refine_candidate_image"] = img
                st.toast(t("refine_candidate_sent_toast"))
        else:
            st.error(t("error_decode", id=candidate_id))
    else:
        st.warning(t("warning_no_image", id=candidate_id))
    
    # Show evolution timeline in an expander
    stages = get_evolution_stages(result, exp_mode)
    if len(stages) > 1:
        with st.expander(t("evolution_expander", n=len(stages)), expanded=False):
            st.caption(t("evolution_caption"))
            
            for idx, stage in enumerate(stages):
                st.markdown(f"### {stage['name']}")
                st.caption(stage['description'])
                
                # Display the image for this stage
                stage_img = base64_to_image(result.get(stage['image_key']))
                if stage_img:
                    st.image(stage_img, width="stretch")
                
                # Show description
                if stage['desc_key'] in result:
                    with st.expander(t("description_expander"), expanded=False):
                        cleaned_desc = clean_text(result[stage['desc_key']])
                        st.write(cleaned_desc)
                
                # Show critic suggestions if available
                if 'suggestions_key' in stage and stage['suggestions_key'] in result:
                    suggestions = result[stage['suggestions_key']]
                    with st.expander(t("critic_suggestions_expander"), expanded=False):
                        cleaned_sugg = clean_text(suggestions)
                        if cleaned_sugg.strip() == "No changes needed.":
                            st.success(t("no_changes_needed"))
                        else:
                            st.write(cleaned_sugg)
                
                # Add separator between stages (except for the last one)
                if idx < len(stages) - 1:
                    st.divider()
    else:
        # If only one stage, show description in simpler expander
        with st.expander(t("view_description_expander"), expanded=False):
            if final_desc_key and final_desc_key in result:
                # Clean the text to remove invalid UTF-8 characters
                cleaned_desc = clean_text(result[final_desc_key])
                st.write(cleaned_desc)
            else:
                st.info(t("no_description"))

def _render_header():
    """Render title, language selector, and return shared UI state."""
    # Sync language from widget state before any t() calls
    if "lang_selector" in st.session_state:
        st.session_state["language"] = SUPPORTED_LANGUAGES[st.session_state["lang_selector"]]

    # Title row with language popover on the right
    title_col, lang_col = st.columns([8, 1])
    with title_col:
        st.title(t("app_title"))
    with lang_col:
        with st.popover("🌐"):
            lang_display = st.radio(
                t("language_label"),
                list(SUPPORTED_LANGUAGES.keys()),
                index=list(SUPPORTED_LANGUAGES.values()).index(st.session_state.get("language", "ko")),
                key="lang_selector",
            )
            st.session_state["language"] = SUPPORTED_LANGUAGES[lang_display]

    st.caption(t("app_subtitle"))

    _busy = st.session_state.get("processing", False)
    _rec = t("recommended_tag")

    def _clean_selectbox_value(val, valid_options, default_idx=0):
        """Strip recommendation tag from selectbox value on language switch."""
        if val in valid_options:
            return val
        for opt in valid_options:
            if val and val.startswith(opt):
                return opt
        return valid_options[default_idx]

    return _busy, _rec, _clean_selectbox_value


def _render_generation_sidebar(_busy, _rec, _clean):
    """Render Tab 1 sidebar and return settings dict."""
    with st.sidebar:
        st.title(t("sidebar_generation_title"))

        exp_mode_options = ["demo_planner_critic", "demo_full"]
        exp_mode = st.selectbox(
            t("pipeline_mode_label"),
            exp_mode_options,
            index=0,
            key="tab1_exp_mode",
            format_func=lambda x: f"{x} {_rec}" if x == exp_mode_options[0] else x,
            help=t("pipeline_mode_help")
        )
        exp_mode = _clean(exp_mode, exp_mode_options)

        mode_info = {
            "demo_planner_critic": t("pipeline_planner_critic"),
            "demo_full": t("pipeline_full")
        }
        st.info(t("pipeline_info", pipeline=mode_info[exp_mode]))

        retrieval_options = ["auto", "manual", "random", "none"]
        retrieval_setting = st.selectbox(
            t("retrieval_label"),
            retrieval_options,
            index=0,
            key="tab1_retrieval_setting",
            format_func=lambda x: f"{x} {_rec}" if x == retrieval_options[0] else x,
            help=t("retrieval_help")
        )
        retrieval_setting = _clean(retrieval_setting, retrieval_options)

        num_candidates = st.number_input(
            t("num_candidates_label"),
            min_value=1,
            max_value=20,
            value=4,
            key="tab1_num_candidates",
            help=t("num_candidates_help") + f" ({_rec}: 4)"
        )

        aspect_ratio = st.selectbox(
            t("aspect_ratio_label"),
            ASPECT_RATIOS,
            key="tab1_aspect_ratio",
            format_func=lambda x: f"{x} {_rec}" if x == ASPECT_RATIOS[0] else x,
            help=t("aspect_ratio_help")
        )
        aspect_ratio = _clean(aspect_ratio, ASPECT_RATIOS)

        max_critic_rounds = st.number_input(
            t("max_critic_rounds_label"),
            min_value=1,
            max_value=5,
            value=1,
            key="tab1_max_critic_rounds",
            help=t("max_critic_rounds_help") + f" ({_rec}: 1)"
        )

        default_model = get_config_val("defaults", "model_name", "MODEL_NAME", "YOUR_MODEL_NAME_HERE")
        options = [default_model] if default_model else ["YOUR_MODEL_NAME_HERE"]

        model_name = st.selectbox(
            t("model_name_label"),
            options,
            index=0,
            key="tab1_model_name",
            help=t("model_name_help")
        )

        lang_options = ["Korean (한국어)", "English"]
        diagram_language = st.selectbox(
            t("diagram_language_label"),
            lang_options,
            index=0,
            key="tab1_diagram_language",
            format_func=lambda x: f"{x} {_rec}" if x == lang_options[0] else x,
            help=t("diagram_language_help"),
        )
        diagram_language = _clean(diagram_language, lang_options)
        diagram_lang_code = "ko" if "Korean" in diagram_language else "en"

    return {
        "exp_mode": exp_mode,
        "mode_info": mode_info,
        "retrieval_setting": retrieval_setting,
        "num_candidates": num_candidates,
        "aspect_ratio": aspect_ratio,
        "max_critic_rounds": max_critic_rounds,
        "model_name": model_name,
        "diagram_lang_code": diagram_lang_code,
    }


def _render_generation_tab(tab, _busy, _rec, _clean):
    """Render the full Generation tab (Tab 1)."""
    with tab:
        st.info(t("generate_header"))

        cfg = _render_generation_sidebar(_busy, _rec, _clean)
        exp_mode = cfg["exp_mode"]
        mode_info = cfg["mode_info"]

        st.divider()

        # Input section
        st.markdown(t("input_header"))

        input_mode = st.radio(
            t("input_mode_label"),
            [t("input_mode_simple"), t("input_mode_direct"), t("input_mode_template")],
            index=0,
            horizontal=True,
            key="input_mode",
            help=t("input_mode_help"),
        )

        if input_mode == t("input_mode_simple"):
            st.caption(t("simple_mode_caption"))

            # ── PDF Upload & Analysis ──
            pdf_file = st.file_uploader(
                t("pdf_upload_label"),
                type=["pdf"],
                key="pdf_uploader",
                help=t("pdf_upload_help"),
            )

            if pdf_file is not None:
                # Detect file change and reset suggestions
                file_id = f"{pdf_file.name}_{pdf_file.size}"
                if st.session_state.get("_pdf_file_id") != file_id:
                    st.session_state["_pdf_file_id"] = file_id
                    st.session_state.pop("pdf_suggestions", None)

                # Size check (20 MB)
                if pdf_file.size > 20 * 1024 * 1024:
                    st.error(t("pdf_size_error"))
                elif st.button(t("pdf_analyze_button"), key="pdf_analyze_btn", disabled=_busy):
                    st.session_state["processing"] = True
                    with st.spinner(t("pdf_analyze_spinner")):
                        try:
                            from utils.pdf_analyzer import analyze_pdf_for_diagrams
                            lang = st.session_state.get("language", "ko")
                            pdf_bytes = pdf_file.getvalue()
                            suggestions = run_async(analyze_pdf_for_diagrams(pdf_bytes, language=lang))
                            st.session_state["pdf_suggestions"] = suggestions
                        except Exception as e:
                            if "QUOTA_ZERO" in str(e):
                                st.warning(t("error_quota_zero"))
                            else:
                                st.error(t("pdf_analyze_error", error=e))
                        finally:
                            st.session_state["processing"] = False
                            st.rerun()

            # Show suggestions if available
            if "pdf_suggestions" in st.session_state and st.session_state["pdf_suggestions"]:
                suggestions = st.session_state["pdf_suggestions"]
                st.markdown(t("pdf_suggestions_header"))
                selected = []
                for i, s in enumerate(suggestions):
                    section_tag = f" [{s['section']}]" if s.get("section") else ""
                    label = f"**{s['title']}**{section_tag}: {s['description']}"
                    if st.checkbox(label, value=True, key=f"pdf_sugg_{i}"):
                        selected.append(s)

                if selected and st.button(t("pdf_use_selected_button"), key="pdf_use_btn", type="primary", width="stretch"):
                    lines = []
                    for s in selected:
                        lines.append(f"- {s['title']}: {s['description']}")
                    st.session_state["simple_desc_input"] = "\n".join(lines)
                    st.session_state.pop("pdf_suggestions", None)
                    st.rerun()

            # ── Text area ──
            simple_desc = st.text_area(
                t("simple_mode_input_label"),
                height=100,
                placeholder=t("simple_mode_placeholder"),
                key="simple_desc_input",
            )
            if st.button(t("simple_mode_generate_button"), key="simple_gen_btn", type="primary", width="stretch", disabled=_busy):
                if simple_desc.strip():
                    st.session_state["processing"] = True
                    with st.spinner(t("simple_mode_spinner")):
                        try:
                            from utils.smart_input import generate_smart_input
                            lang = st.session_state.get("language", "en")
                            result = run_async(generate_smart_input(simple_desc, language=lang))
                            st.session_state["method_content"] = result["method"]
                            st.session_state["caption"] = result["caption"]
                        except Exception as e:
                            if "QUOTA_ZERO" in str(e):
                                st.warning(t("error_quota_zero"))
                            else:
                                st.error(t("simple_mode_api_error", error=e))
                        finally:
                            st.session_state["processing"] = False
                            st.rerun()
                else:
                    st.error(t("simple_mode_empty_error"))

        elif input_mode == t("input_mode_template"):
            from input_templates import INPUT_TEMPLATES
            st.caption(t("template_mode_caption"))
            template_names = list(INPUT_TEMPLATES.keys())
            selected_template = st.selectbox(
                t("template_mode_select_label"),
                template_names,
                key="template_selector",
            )
            tmpl = INPUT_TEMPLATES[selected_template]
            lang = st.session_state.get("language", "en")
            field_values = {}
            for field in tmpl["fields"]:
                label = field["label_ko"] if lang == "ko" else field["label"]
                field_values[field["key"]] = st.text_input(
                    label,
                    placeholder=field.get("placeholder_ko", field.get("placeholder", "")) if lang == "ko" else field.get("placeholder", ""),
                    key=f"tmpl_{field['key']}",
                )
            if st.button(t("template_mode_apply_button"), key="tmpl_apply_btn"):
                filled = {k: v for k, v in field_values.items() if v.strip()}
                if filled:
                    method_text = tmpl["method_template"].format(**{k: field_values.get(k, "") for k in [f["key"] for f in tmpl["fields"]]})
                    caption_text = tmpl["caption_template"].format(**{k: field_values.get(k, "") for k in [f["key"] for f in tmpl["fields"]]})
                    st.session_state["method_content"] = method_text
                    st.session_state["caption"] = caption_text
                    st.rerun()
                else:
                    st.error(t("template_mode_empty_error"))

        # ── Direct Input (always shown) ──
        example_keys = list(EXAMPLE_TEMPLATES.keys())
        lang = st.session_state.get("language", "ko")

        def _example_display(name):
            if name == t("example_none"):
                return name
            if lang == "ko":
                return EXAMPLE_DISPLAY_NAMES_KO.get(name, name)
            return name

        example_names = [t("example_none")] + example_keys
        selected_example = st.selectbox(
            t("example_selector_label"),
            example_names,
            key="example_selector",
            format_func=_example_display,
        )

        if selected_example != t("example_none") and selected_example in EXAMPLE_TEMPLATES:
            method_value = EXAMPLE_TEMPLATES[selected_example]["method"]
            caption_value = EXAMPLE_TEMPLATES[selected_example]["caption"]
        else:
            method_value = st.session_state.get("method_content", "")
            caption_value = st.session_state.get("caption", "")

        col_input1, col_input2 = st.columns([3, 2])

        with col_input1:
            method_content = st.text_area(
                t("method_content_label"),
                value=method_value,
                height=250,
                placeholder=t("method_content_placeholder"),
                help=t("method_content_help"),
            )

        with col_input2:
            caption = st.text_area(
                t("caption_label"),
                value=caption_value,
                height=250,
                placeholder=t("caption_placeholder"),
                help=t("caption_help"),
            )

        # Process button
        if st.button(t("generate_button"), type="primary", width="stretch", disabled=_busy):
            if not method_content or not caption:
                st.error(t("error_missing_input"))
            else:
                st.session_state["processing"] = True
                st.session_state["method_content"] = method_content
                st.session_state["caption"] = caption

                input_data_list = create_sample_inputs(
                    method_content=method_content,
                    caption=caption,
                    aspect_ratio=cfg["aspect_ratio"],
                    num_copies=cfg["num_candidates"],
                    max_critic_rounds=cfg["max_critic_rounds"],
                    diagram_language=cfg["diagram_lang_code"],
                )

                with st.status(t("progress_title"), expanded=True) as status_ui:
                    progress_bar = st.progress(0)
                    log_container = st.container()

                    def on_progress(event, info):
                        if event == "retriever_start":
                            log_container.write(t("progress_retriever_start"))
                        elif event == "retriever_done":
                            log_container.write(t("progress_retriever_done", n=info["refs_count"]))
                        elif event == "candidate_done":
                            done = info["completed"]
                            total = info["total"]
                            progress_bar.progress(done / total, text=t("progress_candidate", done=done, total=total))
                            log_container.write(t("progress_candidate_log", done=done, total=total))

                    try:
                        results = run_async(process_parallel_candidates(
                            input_data_list,
                            exp_mode=exp_mode,
                            retrieval_setting=cfg["retrieval_setting"],
                            model_name=cfg["model_name"],
                            progress_callback=on_progress,
                        ))
                        st.session_state["results"] = results
                        st.session_state["exp_mode"] = exp_mode
                        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state["timestamp"] = timestamp_str

                        try:
                            results_dir = Path(__file__).parent / "results" / "demo"
                            results_dir.mkdir(parents=True, exist_ok=True)
                            json_filename = results_dir / f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

                            with open(json_filename, "w", encoding="utf-8", errors="surrogateescape") as f:
                                json_string = json.dumps(results, ensure_ascii=False, indent=4)
                                json_string = json_string.encode("utf-8", "ignore").decode("utf-8")
                                f.write(json_string)

                            st.session_state["json_file"] = str(json_filename)
                            st.success(t("success_generated", n=len(results)))
                            st.info(t("info_saved", name=json_filename.name))
                        except Exception as e:
                            st.warning(t("warning_save_failed", n=len(results), error=e))
                        status_ui.update(label=t("progress_complete", n=len(results)), state="complete", expanded=False)
                    except Exception as e:
                        status_ui.update(label=t("progress_error"), state="error", expanded=True)
                        if "QUOTA_ZERO" in str(e):
                            st.warning(t("error_quota_zero"))
                        else:
                            st.error(t("error_processing", error=e))
                            import traceback
                            st.code(traceback.format_exc())
                    finally:
                        st.session_state["processing"] = False

        # Display results
        if "results" in st.session_state and st.session_state["results"]:
            results = st.session_state["results"]
            current_mode = st.session_state.get("exp_mode", exp_mode)
            timestamp = st.session_state.get("timestamp", "N/A")

            st.divider()
            st.markdown(t("results_header"))
            st.caption(t("results_caption", timestamp=timestamp, pipeline=mode_info.get(current_mode, current_mode)))

            if "json_file" in st.session_state:
                json_file_path = Path(st.session_state["json_file"])
                if json_file_path.exists():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.info(t("info_results_saved", path=json_file_path.relative_to(Path.cwd())))
                    with col2:
                        with open(json_file_path, "r", encoding="utf-8") as f:
                            json_data = f.read()
                        st.download_button(
                            label=t("download_json"),
                            data=json_data,
                            file_name=json_file_path.name,
                            mime="application/json",
                            width="stretch"
                        )

            num_cols = RESULTS_GRID_COLS
            num_results = len(results)

            for row_start in range(0, num_results, num_cols):
                cols = st.columns(num_cols)
                for col_idx in range(num_cols):
                    result_idx = row_start + col_idx
                    if result_idx < num_results:
                        with cols[col_idx]:
                            display_candidate_result(results[result_idx], result_idx, current_mode)

            # ZIP download
            st.divider()
            st.markdown(t("batch_download_header"))

            try:
                import zipfile

                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    task_name = "diagram"

                    for candidate_id, result in enumerate(results):
                        final_image_key = None

                        for round_idx in range(MAX_CRITIC_ROUNDS_CHECK - 1, -1, -1):
                            image_key = f"target_{task_name}_critic_desc{round_idx}_base64_jpg"
                            if image_key in result and result[image_key]:
                                final_image_key = image_key
                                break

                        if not final_image_key:
                            if current_mode == "demo_full":
                                final_image_key = f"target_{task_name}_stylist_desc0_base64_jpg"
                            else:
                                final_image_key = f"target_{task_name}_desc0_base64_jpg"

                        if final_image_key and final_image_key in result:
                            img = base64_to_image(result[final_image_key])
                            if img:
                                img_buffer = BytesIO()
                                img.save(img_buffer, format="PNG")
                                zip_file.writestr(
                                    f"candidate_{candidate_id}.png",
                                    img_buffer.getvalue()
                                )

                zip_buffer.seek(0)
                st.download_button(
                    label=t("download_zip"),
                    data=zip_buffer.getvalue(),
                    file_name=f"papervizagent_candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    width="stretch"
                )
                st.success(t("zip_ready"))
            except Exception as e:
                st.error(t("error_zip", error=e))


def _render_refinement_tab(tab, _busy, _rec, _clean):
    """Render the full Refinement tab (Tab 2)."""
    with tab:
        st.info(t("refine_header"))

        # Sidebar for refinement settings
        with st.sidebar:
            st.title(t("sidebar_refine_title"))

            refine_resolution = st.selectbox(
                t("target_resolution_label"),
                RESOLUTIONS,
                index=0,
                key="refine_resolution",
                format_func=lambda x: f"{x} {_rec}" if x == RESOLUTIONS[0] else x,
                help=t("target_resolution_help")
            )
            refine_resolution = _clean(refine_resolution, RESOLUTIONS)

            refine_aspect_ratio = st.selectbox(
                t("aspect_ratio_label"),
                ASPECT_RATIOS,
                index=0,
                key="refine_aspect_ratio",
                format_func=lambda x: f"{x} {_rec}" if x == ASPECT_RATIOS[0] else x,
                help=t("refine_aspect_ratio_help")
            )
            refine_aspect_ratio = _clean(refine_aspect_ratio, ASPECT_RATIOS)

            num_rounds = st.slider(
                t("refine_rounds"),
                min_value=1,
                max_value=3,
                value=1,
                key="refine_num_rounds",
                help=t("refine_rounds_help"),
            )

        st.divider()

        # Upload section
        st.markdown(t("upload_header"))
        uploaded_file = st.file_uploader(
            t("file_uploader_label"),
            type=["png", "jpg", "jpeg"],
            help=t("file_uploader_help")
        )

        # Determine image source: uploaded file takes priority, then candidate from Tab 1
        uploaded_image = None

        if uploaded_file is not None:
            # New upload clears candidate image
            st.session_state.pop("refine_candidate_image", None)
            # Reset history when a new file is uploaded
            current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            if st.session_state.get("_refine_file_id") != current_file_id:
                st.session_state["_refine_file_id"] = current_file_id
                st.session_state.pop("refine_history", None)
                st.session_state.pop("refine_history_idx", None)
            uploaded_image = Image.open(uploaded_file)
        elif "refine_candidate_image" in st.session_state:
            st.info(t("refine_candidate_source"))
            candidate_file_id = "candidate_image"
            if st.session_state.get("_refine_file_id") != candidate_file_id:
                st.session_state["_refine_file_id"] = candidate_file_id
                st.session_state.pop("refine_history", None)
                st.session_state.pop("refine_history_idx", None)
            uploaded_image = st.session_state["refine_candidate_image"]

        if uploaded_image is not None:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(t("original_image"))
                st.image(uploaded_image, width="stretch")

            with col2:
                st.markdown(t("edit_instructions"))

                # Preset checkboxes (multi-select)
                preset_items = [
                    ("preset_upscale", "preset_upscale_prompt"),
                    ("preset_fix_content", "preset_fix_content_prompt"),
                    ("preset_fix_text", "preset_fix_text_prompt"),
                    ("preset_bolder_text", "preset_bolder_text_prompt"),
                    ("preset_text_to_english", "preset_text_to_english_prompt"),
                    ("preset_text_to_korean", "preset_text_to_korean_prompt"),
                    ("preset_academic_style", "preset_academic_style_prompt"),
                    ("preset_dark_mode", "preset_dark_mode_prompt"),
                    ("preset_flat_design", "preset_flat_design_prompt"),
                    ("preset_colorful", "preset_colorful_prompt"),
                    ("preset_simplify", "preset_simplify_prompt"),
                    ("preset_add_numbers", "preset_add_numbers_prompt"),
                    ("preset_improve_arrows", "preset_improve_arrows_prompt"),
                    ("preset_improve_contrast", "preset_improve_contrast_prompt"),
                    ("preset_white_bg", "preset_white_bg_prompt"),
                    ("preset_add_border", "preset_add_border_prompt"),
                ]

                st.caption(t("preset_help"))
                selected_prompts = []
                selected_labels = []
                mid = (len(preset_items) + 1) // 2
                pcol1, pcol2 = st.columns(2)
                for idx, (label_key, prompt_key) in enumerate(preset_items):
                    with pcol1 if idx < mid else pcol2:
                        if st.checkbox(t(label_key), key=f"preset_cb_{label_key}", disabled=_busy):
                            selected_prompts.append(t(prompt_key))
                            selected_labels.append(t(label_key))

                if selected_labels:
                    summary = " / ".join(selected_labels)
                    st.markdown(
                        f'<div style="border-left:3px solid #ccc;'
                        f'padding:8px 12px;margin:8px 0;'
                        f'max-height:100px;overflow-y:auto;font-size:0.85em;'
                        f'color:#555;line-height:1.4;">'
                        f'{summary}</div>',
                        unsafe_allow_html=True,
                    )

                preset_combined = "\n\n".join(selected_prompts)

                additional_prompt = st.text_area(
                    t("additional_prompt_label"),
                    height=120,
                    placeholder=t("additional_prompt_placeholder"),
                    help=t("additional_prompt_help"),
                    key="additional_edit_prompt",
                    disabled=_busy,
                )

                base_quality = t("preset_base_quality")
                parts = [p for p in [base_quality, preset_combined, additional_prompt.strip()] if p]
                final_prompt = "\n\n".join(parts)

                # Phase 1: Button click → save params, set busy, rerun
                if st.button(t("refine_button"), type="primary", width="stretch", disabled=_busy):
                    if not final_prompt:
                        st.error(t("error_no_edit_prompt"))
                    else:
                        img_byte_arr = BytesIO()
                        uploaded_image.save(img_byte_arr, format='JPEG')
                        st.session_state["_refine_pending"] = {
                            "image_bytes": img_byte_arr.getvalue(),
                            "edit_prompt": final_prompt,
                            "aspect_ratio": refine_aspect_ratio,
                            "resolution": refine_resolution,
                            "num_rounds": num_rounds,
                        }
                        st.session_state["processing"] = True
                        st.rerun()

                # Phase 2: Execute pending refine
                if st.session_state.get("_refine_pending"):
                    pending = st.session_state.pop("_refine_pending")
                    with st.status(t("refine_progress_title"), expanded=True) as refine_status:
                        log_container = st.container()

                        def on_refine_progress(step, info):
                            if step == "prepare":
                                log_container.write(t("refine_step_prepare"))
                            elif step == "round":
                                log_container.write(t("refine_round_progress", current=info.get("current", 1), total=info.get("total", 1)))
                            elif step == "analyze":
                                log_container.write(t("refine_step_analyze", model=info.get("model", "")))
                            elif step == "analyze_done":
                                log_container.write(t("refine_step_analyze_done", n=info.get("n", 0)))
                                analysis = info.get("analysis", "")
                                if analysis and "NO CORRECTIONS NEEDED" not in analysis.upper():
                                    log_container.code(analysis, language=None)
                            elif step == "api_call":
                                log_container.write(t("refine_step_api", model=info.get("model", "")))
                            elif step == "waiting":
                                log_container.write(t("refine_step_waiting"))
                            elif step == "processing":
                                log_container.write(t("refine_step_processing"))

                        try:
                            round_results, message = run_async(
                                refine_image_with_nanoviz(
                                    image_bytes=pending["image_bytes"],
                                    edit_prompt=pending["edit_prompt"],
                                    aspect_ratio=pending["aspect_ratio"],
                                    image_size=pending["resolution"],
                                    num_rounds=pending.get("num_rounds", 1),
                                    progress_callback=on_refine_progress,
                                )
                            )

                            if round_results:
                                # Append each round result to history
                                history = st.session_state.get("refine_history", [])
                                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                for rb in round_results:
                                    history.append({
                                        "image_bytes": rb,
                                        "timestamp": ts,
                                        "prompt": pending["edit_prompt"][:200],
                                    })
                                # Cap at 10 entries
                                if len(history) > 10:
                                    history = history[-10:]
                                st.session_state["refine_history"] = history
                                st.session_state["refine_history_idx"] = len(history) - 1
                                st.session_state["refine_timestamp"] = ts
                                refine_status.update(label=t("refine_progress_complete", resolution=pending["resolution"]), state="complete", expanded=False)
                            else:
                                refine_status.update(label=t("refine_progress_error"), state="error", expanded=True)
                                st.error(message)
                        except Exception as e:
                            refine_status.update(label=t("refine_progress_error"), state="error", expanded=True)
                            if "QUOTA_ZERO" in str(e):
                                st.warning(t("error_quota_zero"))
                            else:
                                st.error(t("error_refinement", error=e))
                                import traceback
                                st.code(traceback.format_exc())
                        finally:
                            st.session_state["processing"] = False
                            st.rerun()

            # Display refinement history
            history = st.session_state.get("refine_history", [])
            if history:
                st.divider()
                st.markdown(t("refined_result_header"))

                idx = st.session_state.get("refine_history_idx", len(history) - 1)
                idx = max(0, min(idx, len(history) - 1))

                # Navigation bar
                nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
                with nav_col1:
                    if st.button(t("refine_history_prev"), disabled=(idx <= 0 or _busy), key="hist_prev"):
                        st.session_state["refine_history_idx"] = idx - 1
                        st.rerun()
                with nav_col2:
                    st.markdown(
                        f"<div style='text-align:center;font-weight:600;padding:0.4em 0;'>"
                        f"{t('refine_history_counter', current=idx + 1, total=len(history))}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with nav_col3:
                    if st.button(t("refine_history_next"), disabled=(idx >= len(history) - 1 or _busy), key="hist_next"):
                        st.session_state["refine_history_idx"] = idx + 1
                        st.rerun()

                current_entry = history[idx]
                st.caption(t("refined_result_caption", timestamp=current_entry.get("timestamp", "N/A"), resolution=refine_resolution))

                res_col1, res_col2 = st.columns(2)

                with res_col1:
                    st.markdown(t("before_label"))
                    st.image(uploaded_image, width="stretch")

                with res_col2:
                    st.markdown(t("after_label", resolution=refine_resolution))
                    refined_image = Image.open(BytesIO(current_entry["image_bytes"]))
                    st.image(refined_image, width="stretch")

                    st.download_button(
                        label=t("download_refined", resolution=refine_resolution),
                        data=current_entry["image_bytes"],
                        file_name=f"refined_{refine_resolution}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        width="stretch",
                        key="hist_download",
                    )

                # "Refine from this version" button
                if st.button(t("refine_from_this"), disabled=(_busy or not final_prompt), key="refine_from_hist", type="secondary"):
                    st.session_state["_refine_pending"] = {
                        "image_bytes": current_entry["image_bytes"],
                        "edit_prompt": final_prompt,
                        "aspect_ratio": refine_aspect_ratio,
                        "resolution": refine_resolution,
                        "num_rounds": num_rounds,
                    }
                    st.session_state["processing"] = True
                    st.rerun()


def main():
    _busy, _rec, _clean = _render_header()
    tab1, tab2 = st.tabs([t("tab_generate"), t("tab_refine")])
    _render_generation_tab(tab1, _busy, _rec, _clean)
    _render_refinement_tab(tab2, _busy, _rec, _clean)


if __name__ == "__main__":
    main()
