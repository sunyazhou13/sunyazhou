#!/usr/bin/env python3
"""Migrate utterances/gitment comments (Issues) to giscus (Discussions).

Usage:
  GH_TOKEN=xxx python3 migrate_comments_giscus.py           # dry run (analysis only)
  GH_TOKEN=xxx python3 migrate_comments_giscus.py --run     # real migration
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

TOKEN = os.environ.get("GH_TOKEN", "")
if not TOKEN:
    print("ERROR: set GH_TOKEN env var")
    sys.exit(1)
RUN = "--run" in sys.argv

OLD_REPO = "sunyazhou13/gitment-comments"
NEW_REPO_OWNER, NEW_REPO_NAME = "sunyazhou13", "sunyazhou13.github.io"
REPO_ID = "MDEwOlJlcG9zaXRvcnkzODc1NTk1OA=="
CATEGORY_ID = "DIC_kwDOAk9eds4DDwpN"
SITE = "https://www.sunyazhou.com"
CST = timezone(timedelta(hours=8))

POSTS_DIR = "/Users/sunyazhou/Documents/sunyazhou/_posts"


def api_rest(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"bearer {TOKEN}", "User-Agent": "comment-migrator",
        "Accept": "application/vnd.github+json",
    })
    return json.load(urllib.request.urlopen(req))


def api_graphql(query, variables=None):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "comment-migrator"},
    )
    d = json.load(urllib.request.urlopen(req))
    if "errors" in d:
        raise RuntimeError(f"GraphQL error: {d['errors']}")
    return d["data"]


# ---------- Phase 1: read everything ----------

def fetch_all_issues():
    issues = []
    page = 1
    while True:
        batch = api_rest(f"/repos/{OLD_REPO}/issues?state=all&per_page=100&page={page}")
        if not batch:
            break
        issues.extend([i for i in batch if "pull_request" not in i])
        if len(batch) < 100:
            break
        page += 1
    for i in issues:
        i["_comments"] = []
        if i["comments"] > 0:
            i["_comments"] = api_rest(f"/repos/{OLD_REPO}/issues/{i['number']}/comments?per_page=100")
    return issues


def fetch_existing_discussions():
    discs = {}
    cursor = None
    while True:
        q = """
        query($cursor: String) {
          repository(owner: "%s", name: "%s") {
            discussions(first: 100, after: $cursor) {
              pageInfo { hasNextPage endCursor }
              nodes { id number title }
            }
          }
        }""" % (NEW_REPO_OWNER, NEW_REPO_NAME)
        data = api_graphql(q, {"cursor": cursor})
        nodes = data["repository"]["discussions"]["nodes"]
        for n in nodes:
            discs[n["title"]] = n
        pi = data["repository"]["discussions"]["pageInfo"]
        if not pi["hasNextPage"]:
            break
        cursor = pi["endCursor"]
    return discs


# ---------- Phase 2: map old titles to pathnames ----------

FM_TITLE = re.compile(r'^title:\s*["\']?(.+?)["\']?\s*$', re.M)
FM_DATE = re.compile(r'^date:\s*(\d{4})-(\d{2})-(\d{2})', re.M)
PATHNAME_RE = re.compile(r"^\d{4}/\d{2}/[^|]+/$")


def build_post_map():
    """title -> pathname, scanning both zh and en posts."""
    m = {}
    for root, dirs, files in os.walk(POSTS_DIR):
        for f in files:
            if not f.endswith(".md"):
                continue
            p = os.path.join(root, f)
            try:
                text = open(p, encoding="utf-8").read()
            except Exception:
                continue
            mt = FM_TITLE.search(text)
            md = FM_DATE.search(text)
            if not mt or not md:
                continue
            title = mt.group(1).strip()
            slug = f[:-3]
            # Jekyll permalink /:year/:month/:title/ strips the date prefix
            slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug)
            pathname = f"{md.group(1)}/{md.group(2)}/{slug}/"
            m[title] = pathname
            # gitment titles may contain the raw title without quotes variations
    return m


# gitment-era issues whose titles don't match post front-matter titles
MANUAL_MAP = {
    "阿里、字节：一套高效的iOS面试题之我整理的答案": "2020/07/iOSinterviewAnswers1/",
    "抖音的上下滑实现": "2018/11/AwemeTopBottomScrollDemo/",
    "呼吸动画": "2018/09/BreathAnimation/",
    "孙先生的工作笔记": "about/",
    "项目作品": "projects/",
    "iOS抖音视频右小角专辑动画技术实现": "2018/11/AwemeAlbumAnimation/",
    "iOS生成随机颜色代码": "2018/12/RandomColor/",
    "iOS数字跳动动画": "2018/12/NumberRollingAnimation/",
    "markdown插入音乐播放器": "2019/01/MarkdownAudioPlayer/",
    "适配iPhone X": "2018/09/AdaptationiPhoneX/",
}


def normalize_title(t):
    return t.split(" | ")[0].strip()


# ---------- Phase 3: migration ----------

def fmt_dt(iso):
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(CST)
    return dt.strftime("%Y-%m-%d %H:%M")


def comment_body(c):
    return (
        f"> **原评论 @{c['user']['login']}** · {fmt_dt(c['created_at'])} · "
        f"自 utterances 迁移\n\n---\n\n{c['body'].strip()}"
    )


def create_discussion(title, first_comment):
    body = (
        f"# {title}\n\n{SITE}/{title}\n\n"
        f"<sub>此讨论由 utterances 历史评论迁移而来（2026-08-22）。</sub>"
    )
    mut = """
    mutation($repo: ID!, $cat: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {repositoryId: $repo, categoryId: $cat, title: $title, body: $body}) {
        discussion { id number title }
      }
    }"""
    data = api_graphql(mut, {"repo": REPO_ID, "cat": CATEGORY_ID, "title": title, "body": body})
    return data["createDiscussion"]["discussion"]


def add_comment(discussion_id, body):
    mut = """
    mutation($id: ID!, $body: String!) {
      addDiscussionComment(input: {discussionId: $id, body: $body}) {
        comment { id }
      }
    }"""
    api_graphql(mut, {"id": discussion_id, "body": body})


def main():
    print("Fetching old issues ...")
    issues = fetch_all_issues()
    print(f"  {len(issues)} issues, {sum(len(i['_comments']) for i in issues)} comments")

    print("Fetching existing discussions ...")
    discs = fetch_existing_discussions()
    print(f"  {len(discs)} existing discussions")

    post_map = build_post_map()

    # plan: group by pathname (several old issues may target the same article)
    grouped = {}
    skipped_no_comments, unmapped = [], []
    for i in issues:
        raw = i["title"].strip()
        if PATHNAME_RE.match(raw):
            pathname = raw
        else:
            name = normalize_title(raw)
            pathname = post_map.get(name)
            if not pathname:
                pathname = MANUAL_MAP.get(name)
            if not pathname:
                # try fuzzy: strip spaces/punct
                for t, pn in post_map.items():
                    if t.replace(" ", "").lower() == name.replace(" ", "").lower():
                        pathname = pn
                        break
            if not pathname:
                unmapped.append((i["number"], raw, len(i["_comments"])))
                continue
        if not i["_comments"]:
            skipped_no_comments.append((i["number"], pathname))
            continue
        grouped.setdefault(pathname, []).extend(
            {"num": i["number"], **c} for c in i["_comments"])

    plan = []
    for pathname, comments in grouped.items():
        comments.sort(key=lambda c: c["created_at"])
        plan.append({"pathname": pathname, "comments": comments,
                     "existing_disc": discs.get(pathname)})

    print(f"\nPlan: migrate {len(plan)} discussions, "
          f"{sum(len(p['comments']) for p in plan)} comments")
    print(f"Skipped (0 comments): {len(skipped_no_comments)}")
    print(f"Unmapped titles: {len(unmapped)}")
    for n, t, c in unmapped:
        print(f"  #{n} {t!r} ({c} comments)")

    # backup
    backup = [{
        "number": i["number"], "title": i["title"], "state": i["state"],
        "created_at": i["created_at"],
        "comments": [{"user": c["user"]["login"], "created_at": c["created_at"],
                      "body": c["body"]} for c in i["_comments"]],
    } for i in issues]
    with open(os.path.join(os.path.dirname(__file__), "comments_backup.json"), "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=1)
    print("Backup saved: _scripts/comments_backup.json")

    if not RUN:
        print("\n[DRY RUN] no changes made. Re-run with --run to migrate.")
        return

    print("\nMigrating ...")
    ok_disc, ok_comment, fail = 0, 0, []
    log = []
    for p in plan:
        try:
            if p["existing_disc"]:
                disc = p["existing_disc"]
            else:
                disc = create_discussion(p["pathname"], None)
                ok_disc += 1
                time.sleep(0.4)
            for c in p["comments"]:
                add_comment(disc["id"], comment_body(c))
                ok_comment += 1
                time.sleep(0.4)
            src = sorted({c["num"] for c in p["comments"]})
            print(f"  issues {src} -> discussion {disc['number']} {p['pathname']} ({len(p['comments'])} comments)")
            log.append({"discussion": disc["number"], "pathname": p["pathname"],
                        "source_issues": src, "comments": len(p["comments"])})
        except Exception as e:
            fail.append((p["pathname"], str(e)))
            print(f"  FAIL {p['pathname']}: {e}")

    print(f"\nDone. created {ok_disc} discussions, wrote {ok_comment} comments, {len(fail)} failures")
    if fail:
        for f_ in fail:
            print("  FAIL:", f_)
    with open(os.path.join(os.path.dirname(__file__), "migration_log.json"), "w", encoding="utf-8") as f:
        json.dump({"created_discussions": ok_disc, "comments": ok_comment,
                   "failures": fail, "detail": log}, f, ensure_ascii=False, indent=1)
    print("Migration log: _scripts/migration_log.json")


if __name__ == "__main__":
    main()
