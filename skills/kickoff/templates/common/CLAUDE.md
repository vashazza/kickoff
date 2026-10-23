# {{NAME}}

작업을 시작하기 전에 `HANDOFF.md`를 먼저 읽는다. 규칙·데이터 명세·폴더 구조·첫 마일스톤이 거기 있다.
구조화된 제약은 `constraints.yaml`, 원문 규칙은 `docs/`.

## 절대 규칙
<!-- kickoff가 constraints.yaml traps 중 가장 치명적인 2~3개를 한 줄씩 채운다 -->
- `data/raw/`는 수정하지 않는다. 원본 압축파일은 삭제하지 않는다.

## 작업 습관
- 실험이 끝나면 `logs/research_log.md`에 항목을 추가한다 (research-log 스킬).
- 실험 산출물은 `output/exp_NN/`에 둔다. 번호는 연구일지와 같게.
- 새로 알게 된 규칙 해석·결정은 `HANDOFF.md` 해당 섹션과 `constraints.yaml`을 함께 고친다.
