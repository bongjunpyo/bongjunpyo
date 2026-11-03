import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from update_readme import parse_response, render, replace_block, select_recent  # noqa: E402

LOGIN = "bongjunpyo"


def repo(nwo, last, private=False):
    return {
        "nameWithOwner": nwo,
        "name": nwo.split("/")[1],
        "url": f"https://github.com/{nwo}",
        "isPrivate": private,
        "last": last,
    }


def test_parse_response_flattens_graphql_payload():
    payload = {
        "data": {
            "user": {
                "contributionsCollection": {
                    "commitContributionsByRepository": [
                        {
                            "repository": {
                                "nameWithOwner": "bongjunpyo/Sunny",
                                "name": "Sunny",
                                "url": "https://github.com/bongjunpyo/Sunny",
                                "isPrivate": False,
                            },
                            "contributions": {"nodes": [{"occurredAt": "2026-11-03T03:00:00Z"}]},
                        }
                    ]
                }
            }
        }
    }
    assert parse_response(payload) == [repo("bongjunpyo/Sunny", "2026-11-03T03:00:00Z")]


def test_select_recent_drops_private_repos():
    items = [repo("bongjunpyo/ai-one", "2026-11-03T00:00:00Z", private=True),
             repo("bongjunpyo/Sunny", "2026-11-02T00:00:00Z")]
    assert [r["name"] for r in select_recent(items, LOGIN)] == ["Sunny"]


def test_select_recent_drops_profile_repo():
    items = [repo("bongjunpyo/bongjunpyo", "2026-11-03T00:00:00Z"),
             repo("bongjunpyo/Sunny", "2026-11-02T00:00:00Z")]
    assert [r["name"] for r in select_recent(items, LOGIN)] == ["Sunny"]


def test_select_recent_dedupes_same_name_keeping_latest():
    items = [repo("4thIS/opensource_contest_tmax", "2026-08-10T00:00:00Z"),
             repo("bongjunpyo/opensource_contest_tmax", "2026-09-09T00:00:00Z")]
    out = select_recent(items, LOGIN)
    assert [r["nameWithOwner"] for r in out] == ["bongjunpyo/opensource_contest_tmax"]


def test_select_recent_sorts_newest_first_and_limits():
    items = [repo(f"bongjunpyo/r{i}", f"2026-10-{i:02d}T00:00:00Z") for i in range(1, 9)]
    out = select_recent(items, LOGIN, n=5)
    assert [r["name"] for r in out] == ["r8", "r7", "r6", "r5", "r4"]


def test_render_uses_kst_date():
    # 2026-11-02 16:00 UTC == 2026-11-03 01:00 KST
    out = render([repo("bongjunpyo/Sunny", "2026-11-02T16:00:00Z")])
    assert out == "<sub>11-03</sub> [Sunny](https://github.com/bongjunpyo/Sunny)"


def test_replace_block_only_touches_marked_region():
    text = "head\n<!-- recent:start -->\nold\n<!-- recent:end -->\ntail\n"
    assert replace_block(text, "new") == "head\n<!-- recent:start -->\nnew\n<!-- recent:end -->\ntail\n"


def test_replace_block_raises_without_markers():
    with pytest.raises(ValueError):
        replace_block("no markers here", "new")
