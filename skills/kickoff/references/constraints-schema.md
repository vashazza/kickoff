# constraints.yaml 스키마

HANDOFF.md의 모든 규칙 요약은 이 파일에서 나온다. 사람이 읽고 고치기 쉬운 것이 우선이라 YAML로 둔다.
모든 규칙성 항목(`must`, `forbidden`, `allowed`, `traps`)은 `source`를 가진다. 형식: `"<문서명> §조항"` 또는 `"<문서명> p.N"`, 웹이면 URL.

## 공통 필드

```yaml
project:
  name: MyComp                     # 폴더명·패키지명의 기준
  archetype: competition           # competition | research
  one_liner: "문서 1건 → K개 항목 위반 여부(0/1)와 근거 문구"
  deadline: 2026-11-30             # 최종 제출/투고 마감. 모르면 null + open_questions
  first_milestone: "동작하는 베이스라인 submission 1개 + dev 자가 채점"

sources:                           # 이번 kickoff에서 실제로 읽은 문서
  - path: docs/규칙.pdf
    kind: rules                    # rules | eval | data_spec | submission | baseline | paper | proposal | web
    note: "제출 규칙·금지사항"

allowed:      [{rule: "...", source: "..."}]
must:         [{rule: "...", source: "..."}]
forbidden:    [{rule: "...", source: "..."}]

traps:                             # 어기면 무효/0점/재현 실패. kickoff의 핵심 산출물
  - clause: "샘플마다 고정 LLM을 최소 1회 정상 호출해야 함. 규칙만으로 만든 제출물은 무효"
    implication: "게이팅으로 질의 항목이 0개여도 샘플마다 본문을 넣어 1회 호출"
    source: "대회 규칙 §모델"

evaluation:
  metric: "v1~vK 위반(=1) 클래스 F1의 단순 평균 (Macro-F1)"
  local_proxy: "dev 셋 + dev_labels.csv"   # 로컬에서 재현할 방법
  splits: "Public = 테스트 100%, Private = 종료 시점 Public"
  secondary: "근거 문구 정성평가 (상위 팀 대상)"

deliverable:
  format: "output/submission.csv, 열 id,v1~vK,e1~eK"
  checks:                          # 형식 검증기(validate.py)가 그대로 구현할 목록
    - "v는 정수 0/1, 빈칸 금지"
    - "e는 원문 부분문자열, 길이 제한 이하"
    - "UTF-8 no BOM, NFC, 셀 첫 글자 = + @ 금지"

runtime:
  hardware: "GPU 1장, VRAM 48GB급"
  time_limit: "2h"
  network: "차단"
  env_vars: [COMP_DATA_DIR, COMP_OUTPUT_DIR, COMP_MODEL_DIR]
  pinned: ["vllm==X.Y.Z", "torch==X.Y.Z", "python 3.12"]
  local: "로컬 GPU 없음 → --mock + 규칙 경로로 개발"   # 사용자 환경. 모르면 물어본다

reproducibility:
  - rule: "자가 라벨링 코드·프롬프트·모델 버전도 재현 대상"
    where: "scripts/labeling/"
    source: "..."

data:
  - name: dev
    path: data/raw/dev.jsonl.gz
    size: 500
    labels: data/raw/dev_labels.csv
    note: ""

design_principle: "적용 가능성은 코드, 사실·문구 추출은 LLM, 최종 0/1은 후처리 규칙"

open_questions:
  - q: "금액 구간 기준값과 적용 기준일"
    where_to_check: "항목 정의 json의 기준일 필드, 규정 패키지"
    blocking: false                # true면 착수 전에 사용자 확인 필요

assumptions: []                    # 확인 관문을 통과 못 하고 진행한 경우 여기에 기록
```

## research 전용 필드 (archetype: research일 때 추가)

```yaml
research:
  question: "LLM-as-judge가 생성 텍스트 품질을 전문가 평가와 얼마나 일치하게 매기는가?"
  hypotheses:
    - id: H1
      statement: "구조화 루브릭 judge가 자유형 judge보다 전문가 점수와 상관이 높다"
      falsified_if: "Spearman ρ 차이가 부트스트랩 95% CI에서 0을 포함"
  success_criteria: "H1 지지 + 기존 자동 지표 대비 상관 우위"
  baselines:
    - name: "기존 자동 지표 (예: BLEU)"
      source: "논문/코드 링크"
      reproduce_first: true        # 남의 숫자를 가져오기 전에 직접 재현할지
  datasets:
    - name: "[데이터셋]"
      license: "연구용, 재배포 금지"
      split: "공식 split 사용, test는 마지막에 1회"
  metrics: ["Spearman ρ", "Kendall τ", "Cohen κ"]
  statistics: "시드 3개 평균±표준편차, 부트스트랩 1000회 CI"
  seeds: [0, 1, 2]
  compute_budget: "A100 1장, 주당 40 GPU-h"
  venue: "[학회] / 투고 마감 YYYY-MM"
  result_map:                      # 실험 → 논문 표/그림 매핑
    - artifact: "Table 1 (main)"
      experiments: [exp_03, exp_05]
```

## 작성 규칙
- 원문에 없는 값은 쓰지 않는다. 값 대신 `open_questions`에 `where_to_check`와 함께 넣는다.
- 수치·버전·환경변수·파일명은 원문 표기 그대로.
- `traps`는 최소 1개 이상 찾으려고 노력하되, 억지로 만들지 않는다. 없으면 빈 리스트.
- 사용자 환경(로컬 GPU, 마감 내 가용 시간 등)은 문서에 없으므로 짧게 물어보고 `runtime.local`에 적는다.
