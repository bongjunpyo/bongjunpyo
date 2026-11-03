# PITFALLS

## 1. README 미리보기가 실제와 다르게 줄 간격이 벌어짐
- 증상: `gh api markdown` 미리보기에서 `<br>` 줄마다 빈 줄이 하나씩 더 생김
- 원인: `mode=gfm`은 댓글용이라 개행을 `<br>`로 바꿈 → `<br>` + 개행 = `<br><br>`. README는 개행을 그대로 둠
- 어떻게 잡혔나: 렌더 HTML에서 `<br><br>` 확인
- 다음에: README 미리보기는 `mode=markdown`으로 렌더

## 2. 3단 표에서 날짜만 다음 줄로 떨어짐
- 증상: `opensource_contest_tmax <sub>09-09</sub>`처럼 긴 이름 뒤 날짜가 줄바꿈돼 다음 항목처럼 보임
- 원인: 칸 폭 ~250px, 날짜를 끝에 붙임
- 어떻게 잡혔나: 800px 폭 미리보기 스크린샷
- 다음에: 짧은 메타(날짜)는 앞에 둔다 — `<sub>09-09</sub> [name](url)`
