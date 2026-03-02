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
Translation strings for PaperVizAgent Demo UI.
Supports English (en) and Korean (ko).
"""

TRANSLATIONS = {
    "en": {
        # Page / main
        "page_title": "PaperVizAgent Parallel Demo",
        "app_title": "🍌 PaperVizAgent Demo",
        "app_subtitle": "AI-powered scientific diagram generation and refinement",

        # Tabs
        "tab_generate": "Step 1. Generate Diagrams",
        "tab_refine": "Step 2. Refine & Upscale",

        # Tab 1 header
        "generate_header": "Enter your method section and caption below, then generate multiple diagram candidates.",

        # Sidebar – Generation Settings
        "sidebar_generation_title": "⚙️ Generation Settings",
        "pipeline_mode_label": "Pipeline Mode",
        "pipeline_mode_help": "Select which agent pipeline to use",
        "pipeline_planner_critic": "Planner → Visualizer → Critic → Visualizer",
        "pipeline_full": "Retriever → Planner → Stylist → Visualizer → Critic → Visualizer. (The stylist can make the diagram more aesthetically pleasing, but prone to be overly simplified. So we recommend trying both modes and select the best one)",
        "pipeline_info": "**Pipeline:** {pipeline}",
        "retrieval_label": "Retrieval Setting",
        "retrieval_help": "How to retrieve reference diagrams: auto (automatic selection), manual (use specified references), random (random selection), none (no retrieval)",
        "num_candidates_label": "Number of Candidates",
        "num_candidates_help": "How many parallel candidates to generate",
        "aspect_ratio_label": "Aspect Ratio",
        "aspect_ratio_help": "Aspect ratio for the generated diagrams",
        "max_critic_rounds_label": "Max Critic Rounds",
        "max_critic_rounds_help": "Maximum number of critic refinement iterations",
        "model_name_label": "Model Name",
        "model_name_help": "Model name to use for reasoning",

        # Input section
        "input_header": "## 📝 Input",
        "load_example_method": "Load Example (Method)",
        "method_content_label": "Method Section Content (Markdown recommended)",
        "method_content_placeholder": "Paste the method section content here...",
        "method_content_help": "The methodology section from the paper describing the approach to be illustrated.",
        "load_example_caption": "Load Example (Caption)",
        "caption_label": "Figure Caption (Markdown recommended)",
        "caption_placeholder": "Enter the figure caption...",
        "caption_help": "A concise description of the figure to generate, specifying its scope and key components.",

        # Recommended tag
        "recommended_tag": "(Recommended)",

        # Generate button / processing
        "generate_button": "🚀 Generate Candidates",
        "error_missing_input": "Please provide both method content and caption!",
        "spinner_generating": "Generating {n} candidates in parallel... This may take a few minutes.",
        "success_generated": "✅ Successfully generated {n} candidates!",
        "info_saved": "💾 Results saved to: `{name}`",
        "warning_save_failed": "⚠️ Generated {n} candidates, but failed to save JSON: {error}",
        "error_processing": "Error during processing: {error}",

        # Progress tracking
        "progress_title": "Generating diagrams...",
        "progress_retriever_start": "🔍 Searching for reference diagrams...",
        "progress_retriever_done": "✅ Reference search complete ({n} references found)",
        "progress_candidate": "{done}/{total} candidates generated",
        "progress_candidate_log": "✅ Candidate {done}/{total} complete",
        "progress_complete": "✅ Generation complete — {n} candidates",
        "progress_error": "❌ Generation failed",

        # Results section
        "results_header": "## 🎨 Generated Candidates",
        "results_caption": "Generated at: {timestamp} | Pipeline: {pipeline}",
        "info_results_saved": "📄 Results saved to: `{path}`",
        "download_json": "⬇️ Download JSON",
        "batch_download_header": "### 💾 Batch Download",
        "download_zip": "⬇️ Download ZIP",
        "zip_ready": "ZIP file ready for download!",
        "error_zip": "Failed to create ZIP: {error}",

        # Candidate display
        "candidate_caption": "Candidate {id} (Final)",
        "download_candidate": "⬇️ Download",
        "error_decode": "Failed to decode image for Candidate {id}",
        "warning_no_image": "No image generated for Candidate {id}",
        "evolution_expander": "🔄 View Evolution Timeline ({n} stages)",
        "evolution_caption": "See how the diagram evolved through different pipeline stages",
        "description_expander": "📝 Description",
        "critic_suggestions_expander": "💡 Critic Suggestions",
        "no_changes_needed": "✅ No changes needed - iteration stopped.",
        "view_description_expander": "📝 View Description",
        "no_description": "No description available",

        # Evolution stage names
        "stage_planner": "📋 Planner",
        "stage_planner_desc": "Initial diagram plan based on method content",
        "stage_stylist": "✨ Stylist",
        "stage_stylist_desc": "Stylistically refined description",
        "stage_critic_round": "🔍 Critic Round {n}",
        "stage_critic_round_desc": "Refined after critic feedback (iteration {n})",

        # Tab 2 – Refine Image
        "refine_header": "Upload a generated diagram, then refine and upscale to high resolution.",
        "refine_caption": "Upload a diagram, describe desired edits, and generate an improved high-res version",
        "sidebar_refine_title": "✨ Refinement Settings",
        "target_resolution_label": "Target Resolution",
        "target_resolution_help": "Higher resolution takes longer but produces better quality",
        "refine_aspect_ratio_help": "Aspect ratio for the refined image",
        "upload_header": "## 📤 Upload Image",
        "file_uploader_label": "Choose an image file",
        "file_uploader_help": "Supports PNG, JPG formats",
        "original_image": "### Original Image",
        "edit_instructions": "### Edit Instructions",
        "edit_prompt_label": "Describe the changes you want",
        "edit_prompt_placeholder": "E.g., 'Change the color scheme to match academic paper style' or 'Make the text larger and bolder' or 'Keep everything the same but output in higher resolution'",
        "edit_prompt_help": "Use 'Keep everything the same' for upscaling only",
        "additional_prompt_label": "Additional instructions (optional)",
        "additional_prompt_placeholder": "Add extra instructions here. Combined with the preset above.",
        "additional_prompt_help": "Leave empty to use preset only, or add your own instructions to combine with the preset",
        "refine_button": "✨ Refine Image",
        "error_no_edit_prompt": "Please provide edit instructions!",
        "spinner_refining": "Refining image to {resolution} resolution... This may take a minute.",
        "error_refinement": "Error during refinement: {error}",
        "refined_result_header": "## 🎨 Refined Result",
        "refined_result_caption": "Generated at: {timestamp} | Resolution: {resolution}",
        "before_label": "### Before",
        "after_label": "### After ({resolution})",
        "download_refined": "⬇️ Download {resolution} Image",

        # Refine – Preset prompts
        "preset_label": "Quick Edit Presets",
        "preset_help": "Select a common edit action to auto-fill the instructions below",
        "preset_none": "Custom (write your own)",
        "preset_upscale": "Upscale only (keep as-is)",
        "preset_upscale_prompt": "Keep everything exactly the same. Do not change any content, layout, colors, or text. Only output in higher resolution.",
        "preset_fix_text": "Fix text errors",
        "preset_fix_text_prompt": "Carefully examine all text labels, annotations, and captions in the diagram. Fix any typos, misspellings, garbled characters, or grammatically incorrect text. Keep everything else unchanged.",
        "preset_academic_style": "Academic paper style",
        "preset_academic_style_prompt": "Adjust the color scheme and visual style to match modern academic paper standards (clean, professional, muted colors). Keep all content and layout the same.",
        "preset_bolder_text": "Make text larger & bolder",
        "preset_bolder_text_prompt": "Make all text labels, annotations, and captions significantly larger and bolder for better readability. Keep the layout and content unchanged.",
        "preset_simplify": "Simplify & declutter",
        "preset_simplify_prompt": "Simplify the diagram by removing unnecessary decorative elements, reducing visual clutter, and improving whitespace. Keep all essential content intact.",
        "preset_white_bg": "Clean white background",
        "preset_white_bg_prompt": "Replace the background with a clean, pure white background. Remove any background patterns, gradients, or textures. Keep all foreground content unchanged.",

        # Language selector
        "language_label": "🌐 Language",

        # Diagram language selector (Phase 2)
        "diagram_language_label": "Diagram Text Language",
        "diagram_language_help": "Language for text labels in the generated diagram. Korean mode generates diagrams with Korean labels.",

        # Example template selector (Phase 1)
        "example_none": "None",
        "example_selector_label": "Load Example",

        # Input mode (Phase 3)
        "input_mode_label": "Input Mode",
        "input_mode_direct": "Direct Input",
        "input_mode_simple": "Simple Mode",
        "input_mode_template": "Template Mode",
        "input_mode_help": "Direct: paste method section and caption. Simple: describe briefly and let AI generate structured text. Template: fill in a structured template.",

        # Simple mode (Phase 3)
        "simple_mode_caption": "Describe your diagram idea briefly. AI will generate a structured method section and caption for you.",
        "simple_mode_input_label": "Describe the diagram you want to create",
        "simple_mode_placeholder": "e.g., A pipeline diagram showing how a RAG system retrieves documents, re-ranks them, and generates answers\ne.g., A system architecture diagram for a microservices-based e-commerce platform",
        "simple_mode_generate_button": "🤖 Generate Structured Input",
        "simple_mode_spinner": "Generating structured method section and caption...",
        "simple_mode_empty_error": "Please enter a description first!",
        "simple_mode_api_error": "Failed to generate structured input. The model may be temporarily unavailable. Please try again later. ({error})",

        # Template mode (Phase 3)
        "template_mode_caption": "Select a diagram template and fill in the fields. The method section and caption will be generated automatically.",
        "template_mode_select_label": "Select Template",
        "template_mode_apply_button": "📋 Apply Template",
        "template_mode_empty_error": "Please fill in at least one field!",
    },

    "ko": {
        # Page / main
        "page_title": "PaperVizAgent 병렬 데모",
        "app_title": "🍌 PaperVizAgent 데모",
        "app_subtitle": "AI 기반 과학 논문 다이어그램 생성 및 개선",

        # Tabs
        "tab_generate": "Step 1. 다이어그램 생성",
        "tab_refine": "Step 2. 개선 & 업스케일",

        # Tab 1 header
        "generate_header": "방법론 섹션과 캡션을 입력한 뒤, 여러 다이어그램 후보를 생성하세요.",

        # Sidebar – Generation Settings
        "sidebar_generation_title": "⚙️ 생성 설정",
        "pipeline_mode_label": "파이프라인 모드",
        "pipeline_mode_help": "사용할 에이전트 파이프라인을 선택하세요",
        "pipeline_planner_critic": "Planner → Visualizer → Critic → Visualizer",
        "pipeline_full": "Retriever → Planner → Stylist → Visualizer → Critic → Visualizer. (Stylist는 다이어그램을 미학적으로 개선할 수 있지만, 지나치게 단순화될 수 있습니다. 두 모드를 모두 시도하고 최적의 결과를 선택하는 것을 권장합니다)",
        "pipeline_info": "**파이프라인:** {pipeline}",
        "retrieval_label": "검색 설정",
        "retrieval_help": "참조 다이어그램 검색 방법: auto (자동 선택), manual (지정된 참조 사용), random (무작위 선택), none (검색 없음)",
        "num_candidates_label": "후보 수",
        "num_candidates_help": "병렬로 생성할 후보의 수",
        "aspect_ratio_label": "화면 비율",
        "aspect_ratio_help": "생성할 다이어그램의 화면 비율",
        "max_critic_rounds_label": "최대 Critic 라운드",
        "max_critic_rounds_help": "Critic 개선 반복의 최대 횟수",
        "model_name_label": "모델 이름",
        "model_name_help": "추론에 사용할 모델 이름",

        # Input section
        "input_header": "## 📝 입력",
        "load_example_method": "예시 불러오기 (방법론)",
        "method_content_label": "방법론 섹션 내용 (Markdown 권장)",
        "method_content_placeholder": "방법론 섹션 내용을 여기에 붙여넣으세요...",
        "method_content_help": "다이어그램으로 표현할 논문의 방법론 섹션입니다.",
        "load_example_caption": "예시 불러오기 (캡션)",
        "caption_label": "그림 캡션 (Markdown 권장)",
        "caption_placeholder": "그림 캡션을 입력하세요...",
        "caption_help": "생성할 그림의 범위와 핵심 구성요소를 설명하는 간결한 캡션입니다.",

        # Recommended tag
        "recommended_tag": "(추천)",

        # Generate button / processing
        "generate_button": "🚀 후보 생성",
        "error_missing_input": "방법론 내용과 캡션을 모두 입력해주세요!",
        "spinner_generating": "후보 {n}개를 병렬로 생성 중... 몇 분 정도 소요될 수 있습니다.",
        "success_generated": "✅ {n}개의 후보를 성공적으로 생성했습니다!",
        "info_saved": "💾 결과 저장 위치: `{name}`",
        "warning_save_failed": "⚠️ {n}개의 후보를 생성했지만 JSON 저장에 실패했습니다: {error}",
        "error_processing": "처리 중 오류 발생: {error}",

        # Progress tracking
        "progress_title": "다이어그램 생성 중...",
        "progress_retriever_start": "🔍 참조 다이어그램 검색 중...",
        "progress_retriever_done": "✅ 참조 검색 완료 ({n}개 참조 발견)",
        "progress_candidate": "{done}/{total} 후보 생성 완료",
        "progress_candidate_log": "✅ 후보 {done}/{total} 완료",
        "progress_complete": "✅ 생성 완료 — {n}개 후보",
        "progress_error": "❌ 생성 실패",

        # Results section
        "results_header": "## 🎨 생성된 후보",
        "results_caption": "생성 시각: {timestamp} | 파이프라인: {pipeline}",
        "info_results_saved": "📄 결과 저장 위치: `{path}`",
        "download_json": "⬇️ JSON 다운로드",
        "batch_download_header": "### 💾 일괄 다운로드",
        "download_zip": "⬇️ ZIP 다운로드",
        "zip_ready": "ZIP 파일이 다운로드 준비되었습니다!",
        "error_zip": "ZIP 생성 실패: {error}",

        # Candidate display
        "candidate_caption": "후보 {id} (최종)",
        "download_candidate": "⬇️ 다운로드",
        "error_decode": "후보 {id}의 이미지 디코딩에 실패했습니다",
        "warning_no_image": "후보 {id}에 대한 이미지가 생성되지 않았습니다",
        "evolution_expander": "🔄 진화 타임라인 보기 ({n}단계)",
        "evolution_caption": "다이어그램이 파이프라인 단계를 거치며 어떻게 발전했는지 확인하세요",
        "description_expander": "📝 설명",
        "critic_suggestions_expander": "💡 Critic 제안",
        "no_changes_needed": "✅ 변경 불필요 - 반복이 중단되었습니다.",
        "view_description_expander": "📝 설명 보기",
        "no_description": "설명 없음",

        # Evolution stage names
        "stage_planner": "📋 Planner",
        "stage_planner_desc": "방법론 내용 기반 초기 다이어그램 계획",
        "stage_stylist": "✨ Stylist",
        "stage_stylist_desc": "스타일이 개선된 설명",
        "stage_critic_round": "🔍 Critic 라운드 {n}",
        "stage_critic_round_desc": "Critic 피드백 후 개선 (반복 {n})",

        # Tab 2 – Refine Image
        "refine_header": "생성된 다이어그램을 업로드하고, 고해상도(2K/4K)로 개선 및 업스케일하세요.",
        "refine_caption": "다이어그램을 업로드하고 원하는 편집을 설명하면 고해상도 개선 버전을 생성합니다",
        "sidebar_refine_title": "✨ 개선 설정",
        "target_resolution_label": "목표 해상도",
        "target_resolution_help": "높은 해상도는 시간이 더 걸리지만 더 좋은 품질을 제공합니다",
        "refine_aspect_ratio_help": "개선된 이미지의 화면 비율",
        "upload_header": "## 📤 이미지 업로드",
        "file_uploader_label": "이미지 파일 선택",
        "file_uploader_help": "PNG, JPG 형식 지원",
        "original_image": "### 원본 이미지",
        "edit_instructions": "### 편집 지침",
        "edit_prompt_label": "원하는 변경 사항을 설명하세요",
        "edit_prompt_placeholder": "예: '학술 논문 스타일에 맞게 색상 구성 변경' 또는 '텍스트를 더 크고 굵게' 또는 '모든 것을 유지하되 더 높은 해상도로 출력'",
        "edit_prompt_help": "업스케일만 원하면 '모든 것을 동일하게 유지'를 입력하세요",
        "additional_prompt_label": "추가 지침 (선택사항)",
        "additional_prompt_placeholder": "추가 지침을 입력하세요. 위 프리셋과 합쳐져서 전달됩니다.",
        "additional_prompt_help": "프리셋만 사용하려면 비워두세요. 입력하면 프리셋과 함께 전달됩니다.",
        "refine_button": "✨ 이미지 개선",
        "error_no_edit_prompt": "편집 지침을 입력해주세요!",
        "spinner_refining": "{resolution} 해상도로 이미지 개선 중... 약 1분 소요될 수 있습니다.",
        "error_refinement": "개선 중 오류 발생: {error}",
        "refined_result_header": "## 🎨 개선 결과",
        "refined_result_caption": "생성 시각: {timestamp} | 해상도: {resolution}",
        "before_label": "### 이전",
        "after_label": "### 이후 ({resolution})",
        "download_refined": "⬇️ {resolution} 이미지 다운로드",

        # Refine – Preset prompts
        "preset_label": "빠른 편집 프리셋",
        "preset_help": "자주 사용하는 편집 작업을 선택하면 아래 입력란에 자동 채워집니다",
        "preset_none": "직접 작성",
        "preset_upscale": "해상도만 높이기 (내용 유지)",
        "preset_upscale_prompt": "모든 것을 그대로 유지하세요. 내용, 레이아웃, 색상, 텍스트를 변경하지 마세요. 더 높은 해상도로만 출력하세요.",
        "preset_fix_text": "텍스트 오류 수정",
        "preset_fix_text_prompt": "다이어그램의 모든 텍스트 라벨, 주석, 캡션을 꼼꼼히 확인하세요. 오타, 맞춤법 오류, 깨진 문자, 문법 오류를 수정하세요. 나머지는 그대로 유지하세요.",
        "preset_academic_style": "학술 논문 스타일 적용",
        "preset_academic_style_prompt": "현대 학술 논문 기준에 맞게 색상 구성과 시각 스타일을 조정하세요 (깔끔하고, 전문적이며, 차분한 색상). 모든 내용과 레이아웃은 유지하세요.",
        "preset_bolder_text": "텍스트 크게 & 굵게",
        "preset_bolder_text_prompt": "모든 텍스트 라벨, 주석, 캡션을 더 크고 굵게 만들어 가독성을 높이세요. 레이아웃과 내용은 유지하세요.",
        "preset_simplify": "간결하게 정리",
        "preset_simplify_prompt": "불필요한 장식 요소를 제거하고, 시각적 복잡도를 줄이며, 여백을 개선하여 다이어그램을 간결하게 정리하세요. 핵심 내용은 모두 유지하세요.",
        "preset_white_bg": "깨끗한 흰색 배경",
        "preset_white_bg_prompt": "배경을 깨끗한 순백색으로 교체하세요. 배경 패턴, 그라데이션, 텍스처를 제거하세요. 전경 내용은 모두 유지하세요.",

        # Language selector
        "language_label": "🌐 언어",

        # Diagram language selector (Phase 2)
        "diagram_language_label": "다이어그램 텍스트 언어",
        "diagram_language_help": "생성되는 다이어그램의 텍스트 라벨 언어입니다. 한국어 모드는 한글 라벨이 포함된 다이어그램을 생성합니다.",

        # Example template selector (Phase 1)
        "example_none": "없음",
        "example_selector_label": "예시 불러오기",

        # Input mode (Phase 3)
        "input_mode_label": "입력 모드",
        "input_mode_direct": "직접 입력",
        "input_mode_simple": "간편 모드",
        "input_mode_template": "템플릿 모드",
        "input_mode_help": "직접 입력: 방법론 섹션과 캡션을 직접 작성합니다. 간편 모드: 간단히 설명하면 AI가 구조화된 텍스트를 생성합니다. 템플릿 모드: 구조화된 템플릿의 빈칸을 채웁니다.",

        # Simple mode (Phase 3)
        "simple_mode_caption": "다이어그램 아이디어를 간단히 설명하세요. AI가 구조화된 방법론 섹션과 캡션을 생성합니다.",
        "simple_mode_input_label": "만들고 싶은 다이어그램을 설명하세요",
        "simple_mode_placeholder": "예: RAG 시스템이 문서를 검색하고 재순위 지정한 후 답변을 생성하는 파이프라인 다이어그램\n예: 마이크로서비스 기반 이커머스 플랫폼의 시스템 아키텍처 다이어그램",
        "simple_mode_generate_button": "🤖 구조화된 입력 생성",
        "simple_mode_spinner": "구조화된 방법론 섹션과 캡션 생성 중...",
        "simple_mode_empty_error": "먼저 설명을 입력해주세요!",
        "simple_mode_api_error": "구조화된 입력 생성에 실패했습니다. 모델이 일시적으로 사용 불가능할 수 있습니다. 잠시 후 다시 시도해주세요. ({error})",

        # Template mode (Phase 3)
        "template_mode_caption": "다이어그램 템플릿을 선택하고 필드를 채우세요. 방법론 섹션과 캡션이 자동으로 생성됩니다.",
        "template_mode_select_label": "템플릿 선택",
        "template_mode_apply_button": "📋 템플릿 적용",
        "template_mode_empty_error": "최소 하나의 필드를 입력해주세요!",
    },
}
