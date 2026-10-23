---
name: research-log
description: Record an experiment in the project's research log (logs/research_log.md) — add a new exp_NN entry or update one with new results, and keep the summary table at the top in sync. Use after running an experiment, evaluation, or submission, or when the user says "연구일지", "실험 기록", "log this experiment", "exp 기록해줘", or asks to update results of an earlier experiment.
---

# Research log — 실험 기록

kickoff로 만든 프로젝트(또는 같은 마커 구조의 `logs/research_log.md`)에 실험을 기록한다.
기록은 사람이 나중에 "왜 이 결정을 했는지" 되짚는 용도라, 숫자보다 **목적·변경·관찰**이 중요하다.

## 언제 쓰나
- 실험·평가·제출을 한 번 돌렸을 때 (결과가 나빠도, 실패해도 기록)
- 코드만 바뀌고 아직 결과가 없을 때: 항목을 먼저 만들고 결과가 나오면 `--update`
- 이전 실험의 결과·해석을 고칠 때

## 순서
1. 프로젝트의 `HANDOFF.md` 연구일지 섹션에 정한 주 지표 표기를 확인한다.
2. 본문을 scratch 파일에 쓴다. 형식:
   ```markdown
   **목적**: 무엇을 확인하려 했나 (research면 어느 가설 H#)
   **변경 사항**: 바뀐 코드/프롬프트/규칙/설정 — 파일 경로 포함
   **설정**: 데이터(n건), 모델·호출 방식, config 경로, 시드
   **결과**:
   | 지표 | 값 |
   |---|---|
   | <주 지표> | |
   | 최저 3개 항목 / 클래스 | |
   | 실행 시간 | |

   **관찰**: 잘 된 것 / 안 된 것 / 오류 패턴 (예시 id 1~2개)
   **다음 할 일**:
   **산출물**: output/exp_NN/
   ```
   - 숫자는 실제로 돌린 출력에서 옮긴다. 기억이나 추정으로 채우지 않는다. 없으면 빈칸.
   - 이전 실험 대비 변화가 있으면 결과 표에 Δ를 함께 적는다.
3. 기록:
   ```bash
   python3 scripts/log_entry.py --log <project>/logs/research_log.md \
     --title "<한 줄 제목>" --metric "<지표명> <값>" --summary "<요약표용 한 줄>" \
     --body-file <본문 파일> --mkdir <project>/output
   ```
   - 번호는 자동(기존 최대 + 1). 마지막 줄에 `exp_NN`이 출력되니 산출물 폴더명에 그대로 쓴다.
   - 결과 갱신: `--exp NN --update --metric ... --body-file ...` (제목은 생략하면 유지).
   - 로그 파일이 없으면 새로 만든다.
4. research archetype이면, 가설이 지지/반증됐을 때 `HANDOFF.md` §2 가설 표와 §6 결과→논문 매핑의 상태도 고친다.
5. 실험에서 규칙 해석이 바뀌었으면 `constraints.yaml`과 `HANDOFF.md`를 함께 고치고 본문 **관찰**에 적는다.

스크립트 경로는 이 SKILL.md 폴더 기준이다.
