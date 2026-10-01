# -*- coding: utf-8 -*-
"""只改專案描述（project.description），其他一律原樣保留。

整包 PUT /projects 會把版子清空，所以：抓整包 → 存快照 → PUT 專案（只換描述）→
每張版子用抓下來那一份原樣推回去 → 回讀逐張卡、逐條線深度比對。任何一步對不上就停。
用法：python3 desc_push.py <project-id> <描述檔>
"""
import json, os, sys, time, urllib.request, urllib.error

KEY = open(os.path.expanduser("~/.config/larch/key")).read().strip()


def req(pid, method, path="", body=None, etag=None):
    h = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}
    if etag: h["If-Match"] = etag
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(4):
        try:
            r = urllib.request.Request(f"https://larch.ink/api/agent/projects/{pid}{path}", data=data, method=method, headers=h)
            with urllib.request.urlopen(r, timeout=900) as x:
                return x.headers.get("ETag"), json.loads(x.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code != 502 or method == "POST": raise
            print("  502，重試", flush=True); time.sleep(10)  # ponytail: PUT 是整包覆蓋，重送無害


def canon(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def main(pid, desc_file):
    desc = open(desc_file).read().strip()
    et, p = req(pid, "GET"); p = p.get("project", p)
    snap = f"snapshots/desc_push_{pid[8:16]}_{int(time.time())}.json"
    os.makedirs("snapshots", exist_ok=True); json.dump(p, open(snap, "w"), ensure_ascii=False)
    boards = json.loads(json.dumps(p.get("boards", [])))
    print(pid, p["name"], "版子", [(b["name"], len(b["nodes"]), len(b["edges"])) for b in boards], "快照", snap, flush=True)

    p["name"] = desc
    et, _ = req(pid, "PUT", "", {"project": p, "summary": "專案改名：仙泉·香布纏．無雙"}, et)
    for b in boards:
        et, _ = req(pid, "PUT", "/boards/" + b["id"], {"name": b["name"], "nodes": b["nodes"], "edges": b["edges"],
                                                   "summary": "改名後把版子原樣推回"}, et)

    _, q = req(pid, "GET"); q = q.get("project", q)
    got = {b["id"]: b for b in q.get("boards", [])}
    for b in boards:
        g = got.get(b["id"])
        assert g, f"版子 {b['name']} 不見了"
        assert canon(g["nodes"]) == canon(b["nodes"]), f"版子 {b['name']} 的卡片對不上"
        assert canon(g["edges"]) == canon(b["edges"]), f"版子 {b['name']} 的連線對不上"
    for k in ("characters", "media", "variables", "languages", "settings", "description"):
        assert canon(q.get(k)) == canon(p.get(k)), f"{k} 對不上"
    assert q.get("name") == desc, "名稱沒寫進去"
    print("OK：描述已更新；", [(g["name"], len(g["nodes"]), len(g["edges"])) for g in got.values()],
          "卡片與連線逐一相同；角色", len(q.get("characters", [])), "素材", len(q.get("media", [])), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
