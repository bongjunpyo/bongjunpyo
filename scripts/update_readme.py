"""README의 <!-- recent:start/end --> 구간을 최근 커밋한 공개 레포 목록으로 갱신."""
import json
import os
import re
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

START, END = "<!-- recent:start -->", "<!-- recent:end -->"
KST = timezone(timedelta(hours=9))
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      commitContributionsByRepository(maxRepositories: 50) {
        repository { nameWithOwner name url isPrivate }
        contributions(first: 1, orderBy: {field: OCCURRED_AT, direction: DESC}) {
          nodes { occurredAt }
        }
      }
    }
  }
}
"""


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        payload = json.load(res)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload


def parse_response(payload: dict) -> list[dict]:
    rows = payload["data"]["user"]["contributionsCollection"]["commitContributionsByRepository"]
    return [
        {**r["repository"], "last": r["contributions"]["nodes"][0]["occurredAt"]}
        for r in rows
        if r["contributions"]["nodes"]
    ]


def select_recent(items: list[dict], login: str, n: int = 5) -> list[dict]:
    profile = f"{login}/{login}".lower()
    latest: dict[str, dict] = {}
    for r in items:
        if r["isPrivate"] or r["nameWithOwner"].lower() == profile:
            continue
        key = r["name"].lower()  # 같은 이름의 fork/미러는 하나만
        if key not in latest or r["last"] > latest[key]["last"]:
            latest[key] = r
    return sorted(latest.values(), key=lambda r: r["last"], reverse=True)[:n]


def render(items: list[dict]) -> str:
    def day(iso: str) -> str:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(KST).strftime("%m-%d")

    # 날짜를 앞에 둬야 긴 레포명이 줄바꿈돼도 날짜가 떨어지지 않음
    return "<br>\n".join(f"<sub>{day(r['last'])}</sub> [{r['name']}]({r['url']})" for r in items)


def replace_block(text: str, content: str) -> str:
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        raise ValueError("recent 마커가 README에 없음")
    return pattern.sub(lambda _: f"{START}\n{content}\n{END}", text, count=1)


def main() -> None:
    login = os.environ.get("GH_LOGIN", "bongjunpyo")
    readme = Path(__file__).resolve().parents[1] / "README.md"
    items = select_recent(parse_response(fetch(login, os.environ["GITHUB_TOKEN"])), login)
    old = readme.read_text(encoding="utf-8")
    new = replace_block(old, render(items))
    if new != old:
        readme.write_text(new, encoding="utf-8")
    print(render(items))


if __name__ == "__main__":
    main()
