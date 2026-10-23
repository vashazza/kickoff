---
name: kickoff
description: Set up a brand-new competition/hackathon or research-experiment project from its source documents — extract rules and constraints into constraints.yaml, get the user's confirmation, then scaffold the folder, write HANDOFF.md, CLAUDE.md and the research log. Use when the user starts a new 대회·해커톤·경진대회·연구 실험·논문 실험 project, says "kickoff", "초기 세팅", "프로젝트 세팅", "HANDOFF 만들어줘", or drops rule/data-spec documents into an empty project folder.
---

# Kickoff — 프로젝트 초기 세팅

목표: 프로젝트 첫날에 **규칙을 잘못 읽어서 나중에 전부 갈아엎는 일**을 막고, Claude Code가 이후 모든 세션에서 같은 기준으로 일하게 만드는 것.
산출물은 네 가지다: `constraints.yaml`(구조화된 제약), `HANDOFF.md`(사람과 Claude가 먼저 읽는 인수인계 문서), `CLAUDE.md`(HANDOFF를 가리키는 짧은 포인터), `logs/research_log.md`(연구일지).

이 스킬의 경로는 모두 이 SKILL.md가 있는 폴더 기준이다(`scripts/`, `templates/`, `references/`).

## 진행 순서

### 1. 자료 수집 (읽기만, 아무것도 옮기지 않음)
- 프로젝트 폴더를 훑어 규칙·평가·데이터 명세·제출 양식·베이스라인 코드·논문/제안서를 찾는다. 압축파일은 **목록만** 본다(`unzip -l`, `tar -tf`).
- 텍스트가 바로 안 읽히는 문서(pdf, hwp, hwpx, docx, html)는 `python3 scripts/extract_text.py <파일들> --out <scratch 폴더>`로 텍스트를 뽑아 읽는다. 추출 실패 파일은 사용자에게 원문 붙여넣기나 다른 형식을 요청한다.
- 사용자가 웹 페이지(대회 안내 페이지 등)를 링크했으면 그것도 읽는다. 링크가 없는데 규칙 문서도 없으면 사용자에게 받아온다 — 추측으로 규칙을 채우지 않는다.

### 2. archetype 결정
- `competition`: 리더보드·제출 형식·평가 서버·금지 조항이 있는 대회/해커톤.
- `research`: 연구 질문·가설·베이스라인 비교·논문 결과표로 이어지는 실험 프로젝트.
- 둘 다 해당하면(예: 대회 결과로 논문을 쓰려는 경우) `competition`을 기본으로 하고 research 섹션 중 필요한 것(가설, 결과→논문 매핑)을 HANDOFF에 덧붙인다.
- 애매하면 한 번만 묻는다.

### 3. 제약 추출 → `constraints.yaml`
- `references/constraints-schema.md`의 스키마를 따르고, `templates/<archetype>/constraints.yaml`을 뼈대로 쓴다.
- archetype별 체크리스트(`references/checklist-competition.md` 또는 `references/checklist-research.md`)를 **항목마다** 대조하며 원문에서 근거를 찾는다. 원문에 없으면 `open_questions`로 보낸다 — 빈칸을 상식으로 메우지 않는다.
- 모든 must/forbidden/trap 항목에 `source`(문서명·조항·페이지)를 단다. 출처 없는 규칙은 나중에 검증할 수 없다.
- **traps**가 이 스킬의 핵심이다: 읽고 지나치기 쉽지만 어기면 제출 무효·재현 실패·점수 0이 되는 조항, 그리고 그것이 설계에 주는 함의(`implication`)를 적는다. 예: "규칙만으로 만든 제출물은 무효" → "게이팅으로 항목이 0개여도 샘플마다 LLM 1회 호출 유지".

### 4. 확인 관문 (반드시 멈춘다)
`constraints.yaml`을 다 쓴 뒤, 폴더를 만들거나 파일을 옮기기 **전에** 사용자에게 다음만 짧게 보여주고 확인을 받는다:
- 한 줄 요약과 archetype
- traps 전부 (조항 → 함의)
- 핵심 forbidden 3~5개, 평가 지표, 제출/산출물 형식
- open_questions 중 착수 전에 답이 필요한 것

사용자가 고치면 yaml을 고치고 다시 보여준다. 사용자가 자리에 없는 세션이면 가장 보수적인 해석으로 진행하고 HANDOFF 맨 위에 "확인 안 된 가정" 블록을 남긴다.

### 5. 스캐폴드 (결정적 작업은 스크립트로)
```bash
python3 scripts/scaffold.py <project_dir> --archetype <competition|research> --name "<프로젝트명>" --pkg <python_package_name> [--dry-run]
```
- 먼저 `--dry-run`으로 만들 것/건너뛸 것을 확인한 뒤 실행한다.
- 스크립트는 **기존 파일·폴더를 절대 덮어쓰지 않는다.** `.gitignore`는 빠진 줄만 추가한다.
- 압축파일 해제는 스크립트 밖에서 직접 한다: 원본은 `data/`에 그대로 두고 `data/raw/`에 푼다. 원본 삭제 금지.
- 흩어진 규칙 문서는 `docs/`로 **복사**한다(이동 아님).

### 6. HANDOFF.md 작성
- `templates/<archetype>/HANDOFF.md`의 섹션 구조를 그대로 쓰고, 내용은 `constraints.yaml`에서 채운다. 템플릿의 `<!-- -->` 지시문은 지운다.
- 품질 기준은 `references/examples/competition-example.md`. 특히 따라 할 것:
  - §0 한 줄 요약에 "입력 → 출력, 고정된 것, 평가 지표, 첫 목표"가 다 들어간다.
  - §1 "작업 시작 시 해야 할 일"은 Claude Code가 그대로 실행할 수 있는 순서 있는 명령이다.
  - 규칙 요약은 원문을 베끼지 않고, **판정에 쓰이는 형태**(허용/금지, 수치, 환경변수, 시간 제한)로 압축한다.
  - 베이스라인 계획에 **설계 원칙 한 문장**이 있다(무엇을 코드로, 무엇을 모델로 결정하는지).
  - 형식 검증기와 자가 채점기가 첫 마일스톤에 포함된다.
  - 끝에 열린 질문이 "어디서 확인할지"와 함께 있다.
- 길이는 결정에 필요한 만큼만. 원문 규칙 전문은 `docs/`에 두고 HANDOFF는 요약과 포인터만 갖는다.

### 7. 마무리
- `CLAUDE.md`는 scaffold가 만든 포인터를 유지하되, traps 중 가장 치명적인 2~3개를 "절대 규칙"으로 한 줄씩 추가한다(매 세션 자동 로드되므로 짧게).
- `logs/research_log.md`에 exp_00 "프로젝트 세팅" 항목을 research-log 스킬 방식으로 남긴다: `python3 ../research-log/scripts/log_entry.py --log <project>/logs/research_log.md --exp 00 --title "프로젝트 세팅" --metric "-" --summary "kickoff 완료" --body-file <작성한 본문>`.
- 사용자에게는 만든 것 목록 대신 **확인 안 된 가정과 다음 첫 작업 한 가지**만 말한다.

## 하지 말 것
- 확인 관문 전에 폴더 생성·파일 이동·압축 해제.
- 원문에 없는 규칙·수치를 그럴듯하게 채워 넣기 (모르면 open_questions).
- 대회 금지 조항(외부 데이터, 외부 API, 사전학습 가중치 등)을 어기는 도구·데이터를 베이스라인 계획에 넣기.
- 기존 프로젝트 파일 덮어쓰기. 이미 HANDOFF.md가 있으면 `HANDOFF.draft.md`로 쓰고 차이를 보고한다.
