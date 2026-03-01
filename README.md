# <div align="center">PaperBanana 🍌</div>

## 업데이트 및 개선 사항 (원본 PaperVizAgent 소스 대비)

### 2026-03-02: 에이전트 프롬프트 전면 개선 및 Refine 베이스라인 품질 보장

**Planner 프롬프트 강화** (AI 이미지 생성 모델의 빈발 오류 대응)
- `TEXT LABELS`: 라벨 15자 이내 권장, 긴 텍스트 garbling 방지
- `ARROWS & CONNECTIONS`: 모든 연결을 "FROM [A] TO [B]" 형식으로 명시적 기술
- `LAYOUT & HIERARCHY`: 좌→우/상→하 읽기 순서, 주요 요소 크기 차별화, 요소 간 충분한 간격
- `NO HALLUCINATION`: 원본 방법론에 없는 모듈/연결 생성 금지

**Critic 프롬프트 강화** (시각적 결함 검사 체계화)
- `Hallucinated Elements`: 원본 대비 추가/누락 요소 교차 검증
- `Text Overlap`: 텍스트-텍스트, 텍스트-화살표 겹침 검사
- `Arrows & Connections`: 화살표 끊김, 역방향, 과도한 교차 검사
- `Visual Hierarchy`: 읽기 순서 및 크기 계층 검증
- `Color & Contrast`: 어두운 배경, 저대비 텍스트, 네온 색상 플래그

**Refine 베이스라인 품질 프롬프트**
- 모든 편집 요청에 9가지 품질 규칙 자동 삽입 (텍스트 정확성, 화살표 연결, 배경색, 대비, 요소 보존 등)
- 사용자 지침은 `USER INSTRUCTIONS:` 섹션으로 분리하여 기본 규칙과 병합

### 2026-03-02: Refine Image 개선 및 다이어그램 품질 향상

**Refine Image 탭**
- Vertex AI 인증 → API Key 방식으로 전환 (ADC 미설정 에러 해결)
- 빠른 편집 프리셋 드롭다운 추가 (6종: 해상도만 높이기, 텍스트 오류 수정, 학술 스타일 적용, 텍스트 크게/굵게, 간결하게 정리, 흰색 배경)
- 프리셋 + 사용자 추가 지침 합산 구조 (택1이 아닌 병합)

**다이어그램 품질**
- Planner 프롬프트에 `NO REDUNDANCY` 규칙 추가 (개념/용어 1회만 표현)
- Critic 프롬프트에 `Redundancy & Duplication` 검사 + `Conciseness` 규칙 추가

**텍스트 정리**
- 중복/의미 변질된 번역 키 개선 (`method_content_help`, `caption_help`, `refine_caption`, `edit_prompt_help`, `file_uploader_help`)
- Smart Input 에러 핸들링 강화 (재시도 증가, API 실패 시 사용자 친화적 메시지)

### 2026-03-02: 기능 확장 (Phase 1-3)

**Phase 1: 예제 템플릿 확장**
- `demo.py`에 하드코딩되어 있던 예제를 독립 모듈 `example_templates.py`로 분리
- 새 예제 3종 추가: **Transformer Architecture**, **RAG Pipeline**, **Training Pipeline (Encoder-Decoder)**
- 예제 드롭다운이 `EXAMPLE_TEMPLATES` 딕셔너리에서 동적으로 생성 (총 4개)

**Phase 2: 한글 다이어그램 생성**
- `ExpConfig` 및 데이터 파이프라인에 `diagram_language` 필드 추가
- 사이드바에 "다이어그램 텍스트 언어" 선택기 추가 (English / Korean)
- 4개 에이전트에 조건부 한글 언어 지시문 삽입:
  - `planner_agent.py`: 한글 라벨 생성 지시
  - `visualizer_agent.py`: 한글 렌더링 지시
  - `critic_agent.py`: 한글 라벨 보존 지시
  - `stylist_agent.py`: 한글 라벨 보존 지시
- 시스템 프롬프트 번역 불필요 (LLM이 영어 시스템 프롬프트 내에서도 한국어 지시를 이해)

**Phase 3: Smart Input 시스템**
- `st.radio`를 통한 3가지 입력 모드 추가: **직접 입력**, **간편 모드**, **템플릿 모드**
- **간편 모드** (`utils/smart_input.py`): 간단한 설명 입력 → LLM이 구조화된 방법론 섹션 + 캡션 자동 생성
- **템플릿 모드** (`input_templates.py`): Pipeline/Architecture, Comparison/Ablation, Flowchart/Process 빈칸 채우기 템플릿
- 모든 새 UI 요소에 한/영 i18n 완전 지원

### 2026-02-28: 한국어(i18n) 언어 지원
- 한국어 UI 번역 추가 (`translations.py`)
- 데모 UI 헤더에 언어 선택기 추가

---
<div align="center">Dawei Zhu, Rui Meng, Yale Song, Xiyu Wei, Sujian Li, Tomas Pfister and Jinsung yoon
<br><br></div>

</div>
<div align="center">
<a href="https://huggingface.co/papers/2601.23265"><img src="assets/paper-page-xl.svg" alt="Paper page on HF"></a>
<a href="https://huggingface.co/datasets/dwzhu/PaperBananaBench"><img src="assets/dataset-on-hf-xl.svg" alt="Dataset on HF"></a>
</div>

> 안녕하세요! PaperBanana의 원본 버전은 이미 Google-Research에서 [PaperVizAgent](https://github.com/google-research/papervizagent)로 오픈소스 공개되었습니다.
이 저장소는 해당 repo의 내용을 포크한 것으로, 학술 논문 일러스트레이션을 더 잘 지원하기 위해 계속 발전시키는 것을 목표로 합니다. 상당한 진전을 이루었지만, 더 안정적인 생성과 더 다양하고 복잡한 시나리오를 위해서는 아직 갈 길이 멉니다. PaperBanana는 모든 연구자들의 학술 일러스트레이션을 돕기 위한 완전한 오픈소스 프로젝트입니다. 커뮤니티에 기여하는 것이 목표이며, 현재 상업적 용도로 사용할 계획은 없습니다.




**PaperBanana**는 참조 기반 멀티 에이전트 프레임워크로, 학술 논문 일러스트레이션을 자동으로 생성합니다. 전문 에이전트로 구성된 창작 팀처럼 동작하며, 원시 과학 콘텐츠를 **Retriever, Planner, Stylist, Visualizer, Critic** 에이전트의 체계적인 파이프라인을 통해 출판 품질의 다이어그램과 플롯으로 변환합니다. 참조 예제로부터의 인컨텍스트 학습과 반복적 개선을 활용하여 미학적으로 우수하고 의미적으로 정확한 과학 일러스트레이션을 생성합니다.

다음은 PaperBanana가 생성한 다이어그램과 플롯 예시입니다:
![Examples](assets/teaser_figure.jpg)

## PaperBanana 개요

![PaperBanana Framework](assets/method_diagram.png)

PaperBanana는 5개의 전문 에이전트를 체계적인 파이프라인으로 조율하여 고품질 학술 일러스트레이션을 생성합니다:

1. **Retriever Agent**: 큐레이션된 컬렉션에서 가장 관련성 높은 참조 다이어그램을 식별하여 후속 에이전트를 안내합니다
2. **Planner Agent**: 인컨텍스트 학습을 활용하여 방법론 내용과 커뮤니케이션 의도를 종합적인 텍스트 설명으로 변환합니다
3. **Stylist Agent**: 자동 합성된 스타일 가이드라인을 사용하여 학술적 미학 기준에 맞게 설명을 다듬습니다
4. **Visualizer Agent**: 최신 이미지 생성 모델을 사용하여 텍스트 설명을 시각적 결과물로 변환합니다
5. **Critic Agent**: Visualizer와 함께 다중 라운드 반복 개선을 통한 폐루프 정제 메커니즘을 구성합니다

## 빠른 시작

### 1단계: 저장소 클론
```bash
git clone https://github.com/jsonpassion/PaperBanana.git
cd PaperBanana
```

### 2단계: 설정
PaperBanana는 YAML 설정 파일 또는 환경 변수를 통해 API 키를 설정할 수 있습니다.

`configs/model_config.template.yaml` 파일을 `configs/model_config.yaml`로 복사하여 사용자 설정을 외부화하는 것을 권장합니다. 이 파일은 git에서 무시되므로 API 키와 설정이 안전하게 보호됩니다. `model_config.yaml`에서 두 개의 모델 이름(`defaults.model_name`과 `defaults.image_model_name`)을 입력하고, `api_keys` 아래에 최소 하나의 API 키(예: Gemini 모델용 `google_api_key`)를 설정하세요.

다수의 후보를 동시에 생성해야 하는 경우, 높은 동시성을 지원하는 API 키가 필요합니다.

### 3단계: 데이터셋 다운로드
먼저 [PaperBananaBench](https://huggingface.co/datasets/dwzhu/PaperBananaBench)를 다운로드한 후 `data` 디렉토리에 배치합니다 (예: `data/PaperBananaBench/`). 프레임워크는 데이터셋 없이도 Retriever Agent의 few-shot 학습 기능을 건너뛰고 정상적으로 동작하도록 설계되어 있습니다. 원본 PDF에 관심이 있으시다면 [PaperBananaDiagramPDFs](https://huggingface.co/datasets/dwzhu/PaperBananaDiagramPDFs)에서 다운로드하세요.

### 4단계: 환경 설치
1. Python 패키지 관리에 `uv`를 사용합니다. [여기](https://docs.astral.sh/uv/getting-started/installation/)의 안내에 따라 `uv`를 설치하세요.

2. 가상 환경 생성 및 활성화
    ```bash
    uv venv # 현재 디렉토리의 .venv/ 아래에 가상 환경을 생성합니다
    source .venv/bin/activate  # Windows에서는 .venv\Scripts\activate
    ```

3. Python 3.12 설치
    ```bash
    uv python install 3.12
    ```

4. 필요한 패키지 설치
    ```bash
    uv pip install -r requirements.txt
    ```

### PaperBanana 실행

#### 인터랙티브 데모 (Streamlit)
PaperBanana를 가장 쉽게 실행하는 방법은 Streamlit 인터랙티브 데모입니다:
```bash
streamlit run demo.py
```

웹 인터페이스는 두 가지 주요 워크플로를 제공합니다:

**1. 후보 생성 탭**:
- 방법론 섹션 내용(Markdown 권장)을 붙여넣고 그림 캡션을 입력합니다.
- 설정을 구성합니다 (파이프라인 모드, 검색 설정, 후보 수, 화면 비율, Critic 라운드).
- "후보 생성"을 클릭하고 병렬 처리를 기다립니다.
- 결과를 그리드로 확인하고, 진화 타임라인을 보거나 개별 이미지 또는 ZIP 일괄 다운로드가 가능합니다.

**2. 이미지 개선 탭**:
- 생성된 후보 또는 임의의 다이어그램을 업로드합니다.
- 원하는 변경 사항을 설명하거나 업스케일링을 요청합니다.
- 해상도(2K/4K)와 화면 비율을 선택합니다.
- 개선된 고해상도 결과물을 다운로드합니다.

#### 커맨드라인 인터페이스
커맨드라인에서도 PaperBanana를 실행할 수 있습니다:
```bash
# 기본 설정으로 실행
python main.py

# 커스텀 설정으로 실행
python main.py \
  --dataset_name "PaperBananaBench" \
  --task_name "diagram" \
  --split_name "test" \
  --exp_mode "dev_full" \
  --retrieval_setting "auto"
```

**사용 가능한 옵션:**
- `--dataset_name`: 사용할 데이터셋 (기본값: `PaperBananaBench`)
- `--task_name`: 작업 유형 - `diagram` 또는 `plot` (기본값: `diagram`)
- `--split_name`: 데이터셋 분할 (기본값: `test`)
- `--exp_mode`: 실험 모드 (아래 섹션 참조)
- `--retrieval_setting`: 검색 전략 - `auto`, `manual`, `random`, 또는 `none` (기본값: `auto`)

**실험 모드:**
- `vanilla`: 계획이나 개선 없이 직접 생성
- `dev_planner`: Planner → Visualizer만 사용
- `dev_planner_stylist`: Planner → Stylist → Visualizer
- `dev_planner_critic`: Planner → Visualizer → Critic (다중 라운드)
- `dev_full`: 모든 에이전트를 포함한 전체 파이프라인
- `demo_planner_critic`: 데모 모드 (Planner → Visualizer → Critic), 평가 없음
- `demo_full`: 데모 모드 (전체 파이프라인), 평가 없음

### 시각화 도구

파이프라인 진화 및 중간 결과 확인:
```bash
streamlit run visualize/show_pipeline_evolution.py
```
평가 결과 확인:
```bash
streamlit run visualize/show_referenced_eval.py
```

## 프로젝트 구조
```
├── .venv/
│   └── ...
├── data/
│   └── PaperBananaBench/
│       ├── diagram/
│       │   ├── images/
│       │   ├── pdfs/
│       │   ├── test.json
│       │   └── ref.json
│       └── plot/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── retriever_agent.py
│   ├── planner_agent.py
│   ├── stylist_agent.py
│   ├── visualizer_agent.py
│   ├── critic_agent.py
│   ├── vanilla_agent.py
│   └── polish_agent.py
├── prompts/
│   ├── __init__.py
│   ├── diagram_eval_prompts.py
│   └── plot_eval_prompts.py
├── style_guides/
│   ├── generate_category_style_guide.py
│   └── ...
├── utils/
│   ├── __init__.py
│   ├── config.py
│   ├── paperviz_processor.py
│   ├── eval_toolkits.py
│   ├── generation_utils.py
│   ├── image_utils.py
│   └── smart_input.py
├── visualize/
│   ├── show_pipeline_evolution.py
│   └── show_referenced_eval.py
├── scripts/
│   ├── run_main.sh
│   ├── run_demo.sh
├── configs/
│   └── model_config.template.yaml
├── results/
│   ├── PaperBananaBench_diagram/
│   └── parallel_demo/
├── main.py
├── demo.py
├── translations.py
├── example_templates.py
├── input_templates.py
└── README.md
```

## 주요 기능

### 멀티 에이전트 파이프라인
- **참조 기반**: 생성적 검색을 통해 큐레이션된 예제에서 학습
- **반복적 개선**: 점진적 품질 향상을 위한 Critic-Visualizer 루프
- **스타일 인식**: 자동 합성된 미학 가이드라인으로 학술적 품질 보장
- **유연한 모드**: 다양한 사용 사례에 맞는 여러 실험 모드 제공

### 인터랙티브 데모
- **병렬 생성**: 최대 20개의 후보 다이어그램을 동시에 생성
- **파이프라인 시각화**: Planner → Stylist → Critic 단계별 진화 과정 추적
- **고해상도 개선**: 이미지 생성 API를 활용한 2K/4K 업스케일링
- **일괄 내보내기**: 모든 후보를 PNG 또는 ZIP으로 다운로드

### 확장 가능한 설계
- **모듈식 에이전트**: 각 에이전트를 독립적으로 설정 가능
- **작업 지원**: 개념 다이어그램과 데이터 플롯 모두 지원
- **평가 프레임워크**: 다양한 메트릭을 사용한 정답 대비 내장 평가
- **비동기 처리**: 설정 가능한 동시성으로 효율적인 배치 처리

## TODO 리스트
- [ ] 수동 선택 예제 사용 지원 추가. 사용자 친화적인 인터페이스 제공.
- [ ] 통계 플롯 생성 코드 업로드.
- [ ] 스타일 가이드라인 기반 기존 다이어그램 개선 코드 업로드.
- [ ] 컴퓨터 과학 외 분야를 지원하도록 참조 셋 확장.


## 커뮤니티 지원
이 저장소 공개 전후로, 이 작업을 재현하려는 여러 커뮤니티 노력이 있었습니다. 이러한 노력들은 매우 가치 있는 독자적인 관점을 제시합니다. 다음의 훌륭한 기여들을 확인해 보시길 강력히 추천합니다 (빠진 것이 있으면 추가 환영합니다):
- https://github.com/llmsresearch/paperbanana
- https://github.com/efradeca/freepaperbanana

또한 이 방법론의 개발과 함께, 학술 일러스트레이션 자동 생성이라는 같은 주제를 탐구하는 많은 다른 연구들이 있었습니다. 일부는 편집 가능한 생성 그림을 지원하기도 합니다. 이들의 기여는 생태계에 필수적이며 주목할 가치가 있습니다 (마찬가지로 추가 환영합니다):
- https://github.com/ResearAI/AutoFigure-Edit
- https://github.com/OpenDCAI/Paper2Any
- https://github.com/BIT-DataLab/Edit-Banana

전반적으로, 현재 모델의 기본 역량이 학술 일러스트레이션 자동 생성 문제 해결에 한층 더 가까워지게 해준 것에 고무되어 있습니다. 커뮤니티의 지속적인 노력으로, 가까운 미래에 학술 연구 반복과 시각적 커뮤니케이션을 가속화하는 고품질 자동 드로잉 도구를 갖게 될 것이라 믿습니다.

PaperBanana를 더 좋게 만들기 위한 커뮤니티 기여를 환영합니다!

## 라이선스
Apache-2.0

## 인용
이 저장소가 도움이 되셨다면, 다음과 같이 논문을 인용해 주세요:
```bibtex
@article{zhu2026paperbanana,
  title={PaperBanana: Automating Academic Illustration for AI Scientists},
  author={Zhu, Dawei and Meng, Rui and Song, Yale and Wei, Xiyu and Li, Sujian and Pfister, Tomas and Yoon, Jinsung},
  journal={arXiv preprint arXiv:2601.23265},
  year={2026}
}
```

## 면책 조항
이것은 Google의 공식 지원 제품이 아닙니다. 이 프로젝트는 [Google 오픈소스 소프트웨어 취약점 보상 프로그램](https://bughunters.google.com/open-source-security) 대상이 아닙니다.

커뮤니티에 기여하는 것이 목표이며, 현재 상업적 용도로 사용할 계획은 없습니다. 핵심 방법론은 Google 인턴십 기간 중 개발되었으며, 이러한 특정 워크플로에 대해 Google이 특허를 출원했습니다. 이는 오픈소스 연구에는 영향을 미치지 않지만, 유사한 로직을 사용하는 제3자 상업적 응용에는 제한이 있습니다.
