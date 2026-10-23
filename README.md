# kickoff

대회·해커톤과 연구 실험 프로젝트를 **첫날에 제대로** 시작하기 위한 Claude Code 플러그인.

범용 스캐폴더는 폴더만 만들어 준다. kickoff는 그 전에 **규칙·명세 문서를 읽고 제약을 뽑아서 사람에게 확인받은 다음**,
그 제약이 반영된 `HANDOFF.md`와 폴더 구조, 연구일지를 만든다. "규칙만으로 만든 제출물은 무효" 같은 조항을
첫 설계에 반영하는 것이 목적이다.

```
문서 수집 ─▶ constraints.yaml ─▶ [사람 확인] ─▶ scaffold ─▶ HANDOFF.md / CLAUDE.md ─▶ 연구일지 exp_00
```

## 포함된 스킬

| 스킬 | 언제 | 하는 일 |
|---|---|---|
| `kickoff` | 새 프로젝트 시작 | 문서에서 제약 추출 → 확인 관문 → 폴더 생성 → HANDOFF.md·CLAUDE.md 작성 |
| `research-log` | 실험을 돌린 뒤 | `logs/research_log.md`에 exp_NN 항목 추가·갱신, 상단 요약표 자동 정렬 |

두 가지 archetype을 지원한다.

- **competition**: 리더보드·제출 형식·평가 서버·금지 조항이 있는 대회. 제출 형식 검증기와 로컬 자가 채점기를 첫 마일스톤에 넣는다.
- **research**: 가설(반증 조건 포함)·베이스라인 재현·통계·결과→논문 표 매핑이 있는 실험 프로젝트.

## 설치

```bash
# GitHub에 올린 뒤
/plugin marketplace add <github-user>/kickoff
/plugin install kickoff@kickoff

# 또는 로컬 폴더에서
/plugin marketplace add /path/to/kickoff
/plugin install kickoff@kickoff
```

플러그인 없이 쓰려면 `skills/kickoff`와 `skills/research-log`를 `~/.claude/skills/` 아래에 **나란히** 복사한다
(kickoff가 `../research-log/scripts/log_entry.py`를 참조한다).

## 사용

규칙·데이터 문서(zip, pdf, hwpx, docx, md…)를 빈 프로젝트 폴더에 넣고 Claude Code에서:

```
/kickoff
```
또는 "이 대회 초기 세팅해줘", "연구 실험 프로젝트 kickoff 해줘".

**문서가 없어도 된다.** 문서가 없거나 부족하면 인터뷰 모드로 착수에 꼭 필요한 것부터 3~4개씩 묻는다.
- research: 인터뷰가 기본 경로. 연구 질문·가설(반증 조건)·데이터셋·베이스라인·지표 순.
- competition: 규칙 원문은 대체할 수 없어서 먼저 대회 링크나 규칙 붙여넣기를 요청한다. 그래도 없으면 인터뷰로 진행하되 원문 확인을 막는 질문으로 남긴다.
- 답변은 `source: "사용자 답변 (날짜)"`로 기록돼, 나중에 문서와 대조할 수 있다.

Claude가 `constraints.yaml`을 채운 뒤 **traps(어기면 무효가 되는 조항)·핵심 금지사항·평가 지표·막히는 질문**을 보여주고 멈춘다.
확인하면 폴더와 문서를 만든다. 기존 파일은 덮어쓰지 않는다.

실험 후에는 "연구일지에 기록해줘" 또는 `/research-log`.

## 생성되는 구조

<details><summary>competition</summary>

```
PROJECT/
├── HANDOFF.md            # Claude Code가 가장 먼저 읽는 문서
├── CLAUDE.md             # HANDOFF 포인터 + 절대 규칙 (매 세션 자동 로드)
├── constraints.yaml      # 구조화된 제약 (출처 포함)
├── README.md
├── docs/                 # 대회 문서 사본
├── data/{raw,processed,labels}/
├── src/<pkg>/
├── scripts/labeling/     # 자가 라벨링 코드·프롬프트 (재현 대상)
├── submit/
├── output/exp_NN/
├── logs/research_log.md
└── notebooks/
```
</details>

<details><summary>research</summary>

```
PROJECT/
├── HANDOFF.md
├── CLAUDE.md
├── constraints.yaml
├── README.md
├── docs/papers/
├── data/{raw,processed,external}/
├── src/<pkg>/
├── configs/              # 실험 설정 yaml
├── scripts/
├── output/exp_NN/        # 설정 스냅샷 포함
├── logs/research_log.md
├── notebooks/
└── paper/{figures,tables}/
```
</details>

## 파일 구성

```
.claude-plugin/{plugin.json, marketplace.json}
skills/kickoff/
  SKILL.md
  scripts/scaffold.py         # 폴더·기본 파일 생성 (덮어쓰기 없음, --dry-run 지원)
  scripts/extract_text.py     # pdf·hwpx·hwp·docx·html → 텍스트 (표준 라이브러리 위주)
  templates/{competition,research}/{HANDOFF.md, constraints.yaml}
  templates/common/{CLAUDE.md, README.md, research_log.md}
  references/constraints-schema.md
  references/checklist-{competition,research}.md
  references/interview.md            # 문서 없을 때 질문 목록 (Tier 1 → 2)
  references/examples/competition-example.md  # 품질 기준이 된 실제 HANDOFF 예시 (대회 식별 정보 마스킹)
skills/research-log/
  SKILL.md
  scripts/log_entry.py        # 항목 추가·갱신, 요약표 동기화
```

스크립트는 Python 3.9+ 표준 라이브러리만 쓴다. pdf는 `pdftotext` 또는 `pypdf`, 구형 hwp는 `pyhwp`가 있으면 사용한다.

## 확장

새 archetype(예: 오픈소스 기여, 앱 개발)을 추가하려면:
1. `scripts/scaffold.py`의 `LAYOUTS`·`GITIGNORE_EXTRA`에 항목 추가
2. `templates/<archetype>/`에 `HANDOFF.md`, `constraints.yaml`
3. `references/checklist-<archetype>.md`
4. `SKILL.md` 2단계 archetype 목록에 한 줄

## License
MIT
