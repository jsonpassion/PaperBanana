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
from example_templates import EXAMPLE_TEMPLATES

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

def t(key, **kwargs):
    """Return the translated string for the current language."""
    lang = st.session_state.get("language", "en")
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

st.set_page_config(
    layout="wide",
    page_title="PaperVizAgent Parallel Demo",
    page_icon="🍌"
)

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

def create_sample_inputs(method_content, caption, diagram_type="Pipeline", aspect_ratio="16:9", num_copies=10, max_critic_rounds=3, diagram_language="en"):
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

async def process_parallel_candidates(data_list, exp_mode="dev_planner_critic", retrieval_setting="auto", model_name=""):
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
    concurrent_num = 10  # Process all 10 in parallel
    
    async for result_data in processor.process_queries_batch(
        data_list, max_concurrent=concurrent_num, do_eval=False
    ):
        results.append(result_data)
    
    return results

async def refine_image_with_nanoviz(image_bytes, edit_prompt, aspect_ratio="21:9", image_size="2K"):
    """
    Refine an image using Gemini's image editing capability.
    Uses API Key authentication (same as the generation pipeline).

    Args:
        image_bytes: Image data in bytes
        edit_prompt: Text description of desired changes
        aspect_ratio: Output aspect ratio (21:9, 16:9, 3:2)
        image_size: Output resolution (2K or 4K)

    Returns:
        Tuple of (edited_image_bytes, success_message)
    """
    try:
        from google import genai
        from google.genai import types

        # Initialize client with API Key (same as generation pipeline)
        api_key = get_config_val("api_keys", "google_api_key", "GOOGLE_API_KEY", "")
        if not api_key:
            return None, "Google API Key not configured. Set it in configs/model_config.yaml or GOOGLE_API_KEY env var."

        client = genai.Client(api_key=api_key)

        # Prepend baseline quality guardrails to every edit prompt
        baseline_prefix = (
            "BASELINE QUALITY RULES (always apply):\n"
            "- Re-render ALL text labels to be crisp, correctly spelled, and fully legible. "
            "Fix any misspellings or garbled characters.\n"
            "- Ensure no text is cut off at image boundaries.\n"
            "- Ensure no text overlaps with any other element.\n"
            "- Every arrow must clearly connect FROM a source TO a destination. No arrow should end in empty space.\n"
            "- Use a WHITE or very light background suitable for academic publication.\n"
            "- Ensure all text has high contrast against its background.\n"
            "- Do NOT add any new modules, labels, or connections not present in the original.\n"
            "- Do NOT remove any existing content elements.\n"
            "- Do NOT render figure captions or titles inside the image.\n\n"
            "USER INSTRUCTIONS:\n"
        )
        full_prompt = baseline_prefix + edit_prompt

        # Prepare content
        contents = [
            types.Part.from_text(text=full_prompt),
            types.Part.from_bytes(
                mime_type="image/jpeg",
                data=image_bytes
            )
        ]

        # Configure generation
        config = types.GenerateContentConfig(
            temperature=1.0,
            max_output_tokens=8192,
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=image_size,
            ),
        )

        # Generate refined image
        image_model = get_config_val("defaults", "image_model_name", "IMAGE_MODEL_NAME", "")
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=image_model,
            contents=contents,
            config=config
        )

        # Extract image from response
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    edited_image_data = part.inline_data.data

                    if isinstance(edited_image_data, bytes):
                        return edited_image_data, "✅ Image refined successfully!"
                    elif isinstance(edited_image_data, str):
                        return base64.b64decode(edited_image_data), "✅ Image refined successfully!"

        return None, "No image data found in response"

    except Exception as e:
        return None, f"Error: {str(e)}"


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
    for round_idx in range(4):  # Check up to 4 rounds
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
    for round_idx in range(3, -1, -1):  # Check rounds 3, 2, 1, 0
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
            st.image(img, use_container_width=True, caption=t("candidate_caption", id=candidate_id))

            # Add download button
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            st.download_button(
                label=t("download_candidate"),
                data=buffered.getvalue(),
                file_name=f"candidate_{candidate_id}.png",
                mime="image/png",
                key=f"download_candidate_{candidate_id}",
                use_container_width=True
            )
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
                    st.image(stage_img, use_container_width=True)
                
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

def main():
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
                index=list(SUPPORTED_LANGUAGES.values()).index(st.session_state.get("language", "en")),
                key="lang_selector",
            )
            st.session_state["language"] = SUPPORTED_LANGUAGES[lang_display]

    st.markdown(t("app_subtitle"))

    # Create tabs
    tab1, tab2 = st.tabs([t("tab_generate"), t("tab_refine")])
    
    # ==================== TAB 1: Generate Candidates ====================
    with tab1:
        st.markdown(t("generate_header"))

        # Sidebar configuration for Tab 1
        with st.sidebar:
            st.title(t("sidebar_generation_title"))

            exp_mode = st.selectbox(
                t("pipeline_mode_label"),
                ["demo_planner_critic", "demo_full"],
                index=0,
                key="tab1_exp_mode",
                help=t("pipeline_mode_help")
            )

            mode_info = {
                "demo_planner_critic": t("pipeline_planner_critic"),
                "demo_full": t("pipeline_full")
            }
            st.info(t("pipeline_info", pipeline=mode_info[exp_mode]))

            retrieval_setting = st.selectbox(
                t("retrieval_label"),
                ["auto", "manual", "random", "none"],
                index=0,
                key="tab1_retrieval_setting",
                help=t("retrieval_help")
            )

            num_candidates = st.number_input(
                t("num_candidates_label"),
                min_value=1,
                max_value=20,
                value=10,
                key="tab1_num_candidates",
                help=t("num_candidates_help")
            )

            aspect_ratio = st.selectbox(
                t("aspect_ratio_label"),
                ["21:9", "16:9", "3:2"],
                key="tab1_aspect_ratio",
                help=t("aspect_ratio_help")
            )

            max_critic_rounds = st.number_input(
                t("max_critic_rounds_label"),
                min_value=1,
                max_value=5,
                value=3,
                key="tab1_max_critic_rounds",
                help=t("max_critic_rounds_help")
            )

            default_model = get_config_val("defaults", "model_name", "MODEL_NAME", "YOUR_MODEL_NAME_HERE")
            options = ["", default_model] if default_model else ["", "YOUR_MODEL_NAME_HERE"]

            model_name = st.selectbox(
                t("model_name_label"),
                options,
                index=0,
                key="tab1_model_name",
                help=t("model_name_help")
            )

            diagram_language = st.selectbox(
                t("diagram_language_label"),
                ["English", "Korean (한국어)"],
                index=0,
                key="tab1_diagram_language",
                help=t("diagram_language_help"),
            )
            diagram_lang_code = "ko" if "Korean" in diagram_language else "en"
        
        st.divider()

        # Input section
        st.markdown(t("input_header"))

        # Input mode selection
        input_mode = st.radio(
            t("input_mode_label"),
            [t("input_mode_direct"), t("input_mode_simple"), t("input_mode_template")],
            index=0,
            horizontal=True,
            key="input_mode",
            help=t("input_mode_help"),
        )

        if input_mode == t("input_mode_simple"):
            # ── Simple Mode ──
            st.caption(t("simple_mode_caption"))
            simple_desc = st.text_area(
                t("simple_mode_input_label"),
                height=100,
                placeholder=t("simple_mode_placeholder"),
                key="simple_desc_input",
            )
            if st.button(t("simple_mode_generate_button"), key="simple_gen_btn"):
                if simple_desc.strip():
                    with st.spinner(t("simple_mode_spinner")):
                        try:
                            from utils.smart_input import generate_smart_input
                            lang = st.session_state.get("language", "en")
                            result = asyncio.run(generate_smart_input(simple_desc, language=lang))
                            st.session_state["method_content"] = result["method"]
                            st.session_state["caption"] = result["caption"]
                            st.rerun()
                        except Exception as e:
                            st.error(t("simple_mode_api_error", error=e))
                else:
                    st.error(t("simple_mode_empty_error"))

        elif input_mode == t("input_mode_template"):
            # ── Template Mode ──
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

        # ── Direct Input (always shown — acts as the editable text areas) ──
        # Example template names for the dropdown
        example_names = [t("example_none")] + list(EXAMPLE_TEMPLATES.keys())

        col_input1, col_input2 = st.columns([3, 2])

        with col_input1:
            method_example = st.selectbox(
                t("load_example_method"),
                example_names,
                key="method_example_selector",
            )

            if method_example != t("example_none") and method_example in EXAMPLE_TEMPLATES:
                method_value = EXAMPLE_TEMPLATES[method_example]["method"]
            else:
                method_value = st.session_state.get("method_content", "")

            method_content = st.text_area(
                t("method_content_label"),
                value=method_value,
                height=250,
                placeholder=t("method_content_placeholder"),
                help=t("method_content_help"),
            )

        with col_input2:
            caption_example = st.selectbox(
                t("load_example_caption"),
                example_names,
                key="caption_example_selector",
            )

            if caption_example != t("example_none") and caption_example in EXAMPLE_TEMPLATES:
                caption_value = EXAMPLE_TEMPLATES[caption_example]["caption"]
            else:
                caption_value = st.session_state.get("caption", "")

            caption = st.text_area(
                t("caption_label"),
                value=caption_value,
                height=250,
                placeholder=t("caption_placeholder"),
                help=t("caption_help"),
            )
        
        # Process button
        if st.button(t("generate_button"), type="primary", use_container_width=True):
            if not method_content or not caption:
                st.error(t("error_missing_input"))
            else:
                # Save to session state
                st.session_state["method_content"] = method_content
                st.session_state["caption"] = caption
                
                with st.spinner(t("spinner_generating", n=num_candidates)):
                    # Create input data list
                    input_data_list = create_sample_inputs(
                        method_content=method_content,
                        caption=caption,
                        aspect_ratio=aspect_ratio,
                        num_copies=num_candidates,
                        max_critic_rounds=max_critic_rounds,
                        diagram_language=diagram_lang_code,
                    )
                    
                    # Process in parallel
                    try:
                        results = asyncio.run(process_parallel_candidates(
                            input_data_list, 
                            exp_mode=exp_mode, 
                            retrieval_setting=retrieval_setting,
                            model_name=model_name
                        ))
                        st.session_state["results"] = results
                        st.session_state["exp_mode"] = exp_mode
                        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state["timestamp"] = timestamp_str
                        
                        # Save results to JSON file
                        try:
                            # Create results directory if it doesn't exist
                            results_dir = Path(__file__).parent / "results" / "demo"
                            results_dir.mkdir(parents=True, exist_ok=True)
                            
                            # Generate filename with timestamp
                            json_filename = results_dir / f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                            
                            # Save to JSON with proper encoding handling (like main.py)
                            with open(json_filename, "w", encoding="utf-8", errors="surrogateescape") as f:
                                json_string = json.dumps(results, ensure_ascii=False, indent=4)
                                # Clean invalid UTF-8 characters
                                json_string = json_string.encode("utf-8", "ignore").decode("utf-8")
                                f.write(json_string)
                            
                            st.session_state["json_file"] = str(json_filename)
                            st.success(t("success_generated", n=len(results)))
                            st.info(t("info_saved", name=json_filename.name))
                        except Exception as e:
                            st.warning(t("warning_save_failed", n=len(results), error=e))
                    except Exception as e:
                        st.error(t("error_processing", error=e))
                        import traceback
                        st.code(traceback.format_exc())
        
        # Display results
        if "results" in st.session_state and st.session_state["results"]:
            results = st.session_state["results"]
            current_mode = st.session_state.get("exp_mode", exp_mode)
            timestamp = st.session_state.get("timestamp", "N/A")
            
            st.divider()
            st.markdown(t("results_header"))
            st.caption(t("results_caption", timestamp=timestamp, pipeline=mode_info.get(current_mode, current_mode)))
            
            # Show JSON file download if available
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
                            use_container_width=True
                        )
            
            # Display results in a grid (3 columns)
            num_cols = 3
            num_results = len(results)
            
            for row_start in range(0, num_results, num_cols):
                cols = st.columns(num_cols)
                for col_idx in range(num_cols):
                    result_idx = row_start + col_idx
                    if result_idx < num_results:
                        with cols[col_idx]:
                            display_candidate_result(results[result_idx], result_idx, current_mode)
            
            # Add ZIP download button
            st.divider()
            st.markdown(t("batch_download_header"))
            
            try:
                import zipfile
                
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    task_name = "diagram"
                    
                    for candidate_id, result in enumerate(results):
                        
                        # Find the final image key (same logic as display)
                        final_image_key = None
                        
                        # Try to find the last critic round
                        for round_idx in range(3, -1, -1):
                            image_key = f"target_{task_name}_critic_desc{round_idx}_base64_jpg"
                            if image_key in result and result[image_key]:
                                final_image_key = image_key
                                break
                        
                        # Fallback if no critic rounds completed
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
                    use_container_width=True
                )
                st.success(t("zip_ready"))
            except Exception as e:
                st.error(t("error_zip", error=e))
    
    # ==================== TAB 2: Refine Image ====================
    with tab2:
        st.markdown(t("refine_header"))
        st.caption(t("refine_caption"))

        # Sidebar for refinement settings
        with st.sidebar:
            st.title(t("sidebar_refine_title"))

            refine_resolution = st.selectbox(
                t("target_resolution_label"),
                ["2K", "4K"],
                index=0,
                key="refine_resolution",
                help=t("target_resolution_help")
            )

            refine_aspect_ratio = st.selectbox(
                t("aspect_ratio_label"),
                ["21:9", "16:9", "3:2"],
                index=0,
                key="refine_aspect_ratio",
                help=t("refine_aspect_ratio_help")
            )
        
        st.divider()
        
        # Upload section
        st.markdown(t("upload_header"))
        uploaded_file = st.file_uploader(
            t("file_uploader_label"),
            type=["png", "jpg", "jpeg"],
            help=t("file_uploader_help")
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            uploaded_image = Image.open(uploaded_file)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(t("original_image"))
                st.image(uploaded_image, use_container_width=True)

            with col2:
                st.markdown(t("edit_instructions"))

                # Preset prompt dropdown
                preset_options = {
                    t("preset_none"): "",
                    t("preset_upscale"): t("preset_upscale_prompt"),
                    t("preset_fix_text"): t("preset_fix_text_prompt"),
                    t("preset_academic_style"): t("preset_academic_style_prompt"),
                    t("preset_bolder_text"): t("preset_bolder_text_prompt"),
                    t("preset_simplify"): t("preset_simplify_prompt"),
                    t("preset_white_bg"): t("preset_white_bg_prompt"),
                }
                selected_preset = st.selectbox(
                    t("preset_label"),
                    list(preset_options.keys()),
                    key="refine_preset",
                    help=t("preset_help"),
                )
                preset_value = preset_options[selected_preset]

                # Show selected preset as a chip
                if preset_value:
                    st.info(f"**{selected_preset}**: {preset_value[:80]}...")

                additional_prompt = st.text_area(
                    t("additional_prompt_label"),
                    height=120,
                    placeholder=t("additional_prompt_placeholder"),
                    help=t("additional_prompt_help"),
                    key="additional_edit_prompt"
                )

                # Combine: preset + user additional text
                parts = [p for p in [preset_value, additional_prompt.strip()] if p]
                final_prompt = "\n\n".join(parts)

                if st.button(t("refine_button"), type="primary", use_container_width=True):
                    if not final_prompt:
                        st.error(t("error_no_edit_prompt"))
                    else:
                        with st.spinner(t("spinner_refining", resolution=refine_resolution)):
                            try:
                                # Convert PIL image to bytes
                                img_byte_arr = BytesIO()
                                uploaded_image.save(img_byte_arr, format='JPEG')
                                image_bytes = img_byte_arr.getvalue()

                                # Call nanoviz API
                                refined_bytes, message = asyncio.run(
                                    refine_image_with_nanoviz(
                                        image_bytes=image_bytes,
                                        edit_prompt=final_prompt,
                                        aspect_ratio=refine_aspect_ratio,
                                        image_size=refine_resolution
                                    )
                                )
                                
                                if refined_bytes:
                                    st.session_state["refined_image"] = refined_bytes
                                    st.session_state["refine_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                            except Exception as e:
                                st.error(t("error_refinement", error=e))
                                import traceback
                                st.code(traceback.format_exc())
            
            # Display refined result if available
            if "refined_image" in st.session_state:
                st.divider()
                st.markdown(t("refined_result_header"))
                st.caption(t("refined_result_caption", timestamp=st.session_state.get('refine_timestamp', 'N/A'), resolution=refine_resolution))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(t("before_label"))
                    st.image(uploaded_image, use_container_width=True)

                with col2:
                    st.markdown(t("after_label", resolution=refine_resolution))
                    refined_image = Image.open(BytesIO(st.session_state["refined_image"]))
                    st.image(refined_image, use_container_width=True)

                    # Download button
                    st.download_button(
                        label=t("download_refined", resolution=refine_resolution),
                        data=st.session_state["refined_image"],
                        file_name=f"refined_{refine_resolution}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()
