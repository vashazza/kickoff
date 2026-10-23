# 인터뷰 질문 목록 (문서가 없거나 부족할 때)

문서에서 이미 찾은 항목은 건너뛴다. 한 번에 3~4개, Tier 1 → Tier 2 순서.
각 질문 옆의 `→`는 답이 들어갈 constraints.yaml 필드다.
답은 `source: "사용자 답변 (YYYY-MM-DD)"`로 기록한다.

## 공통 (항상 먼저)
1. 이 프로젝트를 한 문장으로 설명하면? 무엇을 입력받아 무엇을 내는지 → `project.one_liner`
2. 마감은 언제인가? (최종 제출 / 투고 / 보고) → `project.deadline`
3. 작업할 환경은? 로컬 GPU 유무, 서버 사용 여부 → `runtime.local`
4. 첫 1~2주 안에 "됐다"고 말할 수 있는 결과물은? → `project.first_milestone`

## competition

### Tier 1 — 이게 없으면 착수 불가
- 대회 페이지 링크나 규칙 원문을 줄 수 있나? (가능하면 인터뷰보다 이것을 우선)
- 평가 지표는? 평균 방식(macro/micro)과 양성 클래스만인지까지 → `evaluation.metric`
- 제출물 형식은? 파일명, 열, 값 타입 → `deliverable.format`, `deliverable.checks`
- 쓸 수 있는/써야 하는 모델이 정해져 있나? 외부 데이터·외부 API·사전학습 가중치 허용 범위는? → `must`, `forbidden`
- 로컬에서 점수를 재볼 수 있는 라벨 데이터가 있나? → `evaluation.local_proxy`

### Tier 2 — 첫 주 안에 필요
- 평가 서버에서 코드가 돌아가나, 결과 파일만 내나? 실행 시간·하드웨어 제한은? → `runtime`
- 수상 시 재현 검증 범위는? (코드, 라벨 생성 과정, 프롬프트) → `reproducibility`
- Public/Private 분할, 2차 평가 유무 → `evaluation.splits`, `evaluation.secondary`
- 제출 횟수 제한 → `must`

## research

### Tier 1 — 이게 없으면 첫 실험을 설계할 수 없음
- 연구 질문을 "무엇을, 무엇과 비교해, 무엇으로 측정"으로 말하면? → `research.question`
- 지금 믿고 있는 가설은? 어떤 결과가 나오면 틀렸다고 인정할 건가? → `research.hypotheses[].falsified_if`
- 쓸 데이터셋은? 이미 접근 가능한가, 라이선스·반출 제한은? → `research.datasets`
- 비교할 베이스라인은? 논문 숫자를 가져올 건가, 직접 재현할 건가? → `research.baselines`
- 주 지표는? → `research.metrics`

### Tier 2 — 첫 실험 전후로 필요
- 시드·반복 횟수, 신뢰구간이나 통계 검정 방식 → `research.statistics`, `research.seeds`
- 데이터 누수 위험: 환자/피험자 단위 분리, 시간 순서, 사전학습 데이터와 겹침 → `traps`
- 투고처와 페이지 제한, 중간 보고 일정 → `research.venue`
- 결과가 들어갈 논문 표/그림 초안 → `research.result_map`
- GPU·API 비용 한도 → `research.compute_budget`
- 지도교수·공동연구자와 이미 합의된 제약(데이터 사용 범위, 실험 분담 등) → `must`
