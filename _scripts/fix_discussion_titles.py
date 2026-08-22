#!/usr/bin/env python3
"""Fix discussion titles that wrongly include the date prefix in the slug,
and verify every discussion title maps to a live URL (200).

Usage: GH_TOKEN=xxx python3 fix_discussion_titles.py [--run]
"""
import json
import os
import re
import sys
import time
import urllib.request

TOKEN = os.environ.get("GH_TOKEN", "")
RUN = "--run" in sys.argv
SITE = "https://www.sunyazhou.com"

DATE_PREFIX = re.compile(r"^(\d{4}/\d{2})/\d{4}-\d{2}-\d{2}-(.+)$")


def gql(query, variables=None):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "fix-titles"},
    )
    d = json.load(urllib.request.urlopen(req))
    if "errors" in d:
        raise RuntimeError(d["errors"])
    return d["data"]


def http_code(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "check"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


# fetch all discussions
nodes, cursor = [], None
while True:
    data = gql("""
    query($cursor: String) {
      repository(owner: "sunyazhou13", name: "sunyazhou13.github.io") {
        discussions(first: 100, after: $cursor) {
          pageInfo { hasNextPage endCursor }
          nodes { id number title body }
        }
      }
    }""", {"cursor": cursor})
    r = data["repository"]["discussions"]
    nodes.extend(r["nodes"])
    if not r["pageInfo"]["hasNextPage"]:
        break
    cursor = r["pageInfo"]["endCursor"]

print(f"Fetched {len(nodes)} discussions")

renamed, bad_url = [], []
for n in nodes:
    t = n["title"]
    if t == "Welcome to sunyazhou13.github.io Discussions!":
        continue
    m = DATE_PREFIX.match(t)
    new_t = f"{m.group(1)}/{m.group(2)}" if m else t
    # verify target URL is live
    url = f"{SITE}/{new_t}"
    code = http_code(url)
    if code != 200:
        bad_url.append((n["number"], new_t, code))
        print(f"  !! #{n['number']} {new_t} -> HTTP {code}")
        continue
    if not m:
        continue
    print(f"  rename #{n['number']}: {t} -> {new_t}")
    if RUN:
        body = (
            f"# {new_t}\n\n{SITE}/{new_t}\n\n"
            f"<sub>此讨论由 utterances 历史评论迁移而来（2026-08-22）。</sub>"
        )
        gql("""
        mutation($id: ID!, $title: String!, $body: String!) {
          updateDiscussion(input: {discussionId: $id, title: $title, body: $body}) {
            discussion { number title }
          }
        }""", {"id": n["id"], "title": new_t, "body": body})
        time.sleep(0.4)
        renamed.append((n["number"], t, new_t))

print(f"\nrenamed: {len(renamed)}, bad urls: {len(bad_url)}")
if not RUN:
    print("[DRY RUN] pass --run to apply")
