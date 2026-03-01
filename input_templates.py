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
Template-based input templates for PaperVizAgent Demo.
Each template defines fields the user fills in, plus method/caption templates
that are populated from those fields.
"""

INPUT_TEMPLATES = {
    "Pipeline / Architecture": {
        "fields": [
            {
                "key": "system_name",
                "label": "System Name",
                "label_ko": "시스템 이름",
                "placeholder": "e.g., ImageSearch Pipeline",
                "placeholder_ko": "예: 이미지 검색 파이프라인",
            },
            {
                "key": "num_stages",
                "label": "Number of Stages",
                "label_ko": "단계 수",
                "placeholder": "e.g., 4",
                "placeholder_ko": "예: 4",
            },
            {
                "key": "stage_names",
                "label": "Stage Names (comma-separated)",
                "label_ko": "단계 이름 (쉼표로 구분)",
                "placeholder": "e.g., Preprocessing, Encoding, Retrieval, Ranking",
                "placeholder_ko": "예: 전처리, 인코딩, 검색, 랭킹",
            },
            {
                "key": "stage_descriptions",
                "label": "Stage Descriptions (comma-separated)",
                "label_ko": "단계 설명 (쉼표로 구분)",
                "placeholder": "e.g., Clean raw data, Embed into vectors, Find top-k matches, Re-rank by relevance",
                "placeholder_ko": "예: 원시 데이터 정리, 벡터 임베딩, 상위 k개 매칭, 관련성 재순위",
            },
            {
                "key": "data_flow",
                "label": "Data Flow Description",
                "label_ko": "데이터 흐름 설명",
                "placeholder": "e.g., Images flow from input through each stage sequentially",
                "placeholder_ko": "예: 이미지가 입력부터 각 단계를 순차적으로 통과",
            },
        ],
        "method_template": (
            "## {system_name}\n\n"
            "We propose {system_name}, a multi-stage pipeline consisting of {num_stages} stages.\n\n"
            "### Stages\n\n"
            "The pipeline comprises the following stages: {stage_names}.\n\n"
            "Each stage performs the following operations: {stage_descriptions}.\n\n"
            "### Data Flow\n\n"
            "{data_flow}"
        ),
        "caption_template": (
            "Figure 1: Overview of the {system_name} pipeline with {num_stages} stages: "
            "{stage_names}. {data_flow}"
        ),
    },
    "Comparison / Ablation": {
        "fields": [
            {
                "key": "study_name",
                "label": "Study Name",
                "label_ko": "연구 이름",
                "placeholder": "e.g., Ablation Study on Attention Mechanisms",
                "placeholder_ko": "예: 어텐션 메커니즘 절제 연구",
            },
            {
                "key": "baseline",
                "label": "Baseline Method",
                "label_ko": "베이스라인 방법",
                "placeholder": "e.g., Standard Multi-Head Attention",
                "placeholder_ko": "예: 표준 멀티헤드 어텐션",
            },
            {
                "key": "variants",
                "label": "Variants to Compare (comma-separated)",
                "label_ko": "비교할 변형 (쉼표로 구분)",
                "placeholder": "e.g., Linear Attention, Sparse Attention, Flash Attention",
                "placeholder_ko": "예: 선형 어텐션, 희소 어텐션, 플래시 어텐션",
            },
            {
                "key": "comparison_criteria",
                "label": "Comparison Criteria",
                "label_ko": "비교 기준",
                "placeholder": "e.g., Accuracy, Latency, Memory Usage",
                "placeholder_ko": "예: 정확도, 지연 시간, 메모리 사용량",
            },
        ],
        "method_template": (
            "## {study_name}\n\n"
            "We conduct a comprehensive comparison study to evaluate different approaches.\n\n"
            "### Baseline\n\n"
            "Our baseline method is {baseline}.\n\n"
            "### Variants\n\n"
            "We compare the following variants: {variants}.\n\n"
            "### Evaluation Criteria\n\n"
            "All methods are evaluated on: {comparison_criteria}."
        ),
        "caption_template": (
            "Figure 1: Comparison of {baseline} against {variants}, "
            "evaluated on {comparison_criteria}."
        ),
    },
    "Flowchart / Process": {
        "fields": [
            {
                "key": "process_name",
                "label": "Process Name",
                "label_ko": "프로세스 이름",
                "placeholder": "e.g., Model Training Workflow",
                "placeholder_ko": "예: 모델 학습 워크플로우",
            },
            {
                "key": "steps",
                "label": "Steps (comma-separated)",
                "label_ko": "단계 (쉼표로 구분)",
                "placeholder": "e.g., Data Collection, Preprocessing, Training, Evaluation, Deployment",
                "placeholder_ko": "예: 데이터 수집, 전처리, 학습, 평가, 배포",
            },
            {
                "key": "decision_points",
                "label": "Decision Points (comma-separated, or 'None')",
                "label_ko": "의사결정 지점 (쉼표로 구분, 또는 '없음')",
                "placeholder": "e.g., Is accuracy > 90%?, Pass quality check?",
                "placeholder_ko": "예: 정확도 > 90%?, 품질 검사 통과?",
            },
            {
                "key": "outcomes",
                "label": "Final Outcomes",
                "label_ko": "최종 결과",
                "placeholder": "e.g., Deployed model serving predictions",
                "placeholder_ko": "예: 배포된 모델이 예측 서빙",
            },
        ],
        "method_template": (
            "## {process_name}\n\n"
            "We describe the end-to-end process for {process_name}.\n\n"
            "### Steps\n\n"
            "The process consists of the following steps: {steps}.\n\n"
            "### Decision Points\n\n"
            "Key decision points include: {decision_points}.\n\n"
            "### Outcomes\n\n"
            "{outcomes}"
        ),
        "caption_template": (
            "Figure 1: Flowchart of the {process_name} process, "
            "showing sequential steps ({steps}) with decision points ({decision_points}), "
            "leading to the final outcome."
        ),
    },
}
