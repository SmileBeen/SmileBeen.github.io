"""허브 데이터 훅.

projects.yml, data/tags.yml, data/<slug>/parts.yml, data/<slug>/episodes/*.md,
docs/blog/posts/*.md 를 읽어서

  /projects/                      모든 프로젝트   (overrides/projects.html)
  /projects/<slug>/               프로젝트 상세   (overrides/project.html)
  /projects/<slug>/epNN/          회차            (overrides/episode.html)
  /tags/                          다루는 것       (overrides/tags.html)
  /parts/                         부품 전체 BOM   (overrides/parts.html)
  /setup/                         개발 환경 목차   (overrides/setup.html)
  /setup/<slug>/                  설치 하나       (overrides/setup-page.html)
  /examples/                      예제 목록       (overrides/examples.html)
  /examples/exNN/                 예제 하나       (overrides/example.html)

페이지를 빌드할 때 만들고, 모든 템플릿에 `hb` 변수로 데이터를 넘겨요.
"""
from __future__ import annotations

import datetime as dt
import logging
import re
from pathlib import Path

import yaml
from mkdocs.structure.files import File
from mkdocs.utils.meta import get_data

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

log = logging.getLogger("mkdocs.hooks.projects")

PROJ_STATUS = {"진행 중": "wip", "준비 중": "todo", "완료": "done"}
EP_STATUS = {"공개": "on", "편집 중": "wip", "촬영 준비": "wip", "준비 중": "todo"}
KIND = {"main": "메인", "side": "사이드"}
EX_STATUS = {"공개": "on", "편집 중": "wip", "촬영 준비": "wip", "준비 중": "todo"}
PART_STATUS = {"보유": "have", "구매 예정": "buy", "나중": "later"}
PART_STATUS_ORDER = ["보유", "구매 예정", "나중"]
PART_CAT_ORDER = ["MCU · 보드", "통신 모듈", "전원 · 제어", "센서", "계측 장비", "기타"]


def _cat_sort(cats):
    return sorted(cats, key=lambda c: (PART_CAT_ORDER.index(c) if c in PART_CAT_ORDER else len(PART_CAT_ORDER), c))

HB: dict = {}


def _yaml(path: Path, default):
    if not path.exists():
        return default
    return yaml.safe_load(path.read_text(encoding="utf-8")) or default


def _date(v) -> dt.date | None:
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if isinstance(v, dict):  # Material blog: date: {created: ...}
        return _date(v.get("created"))
    if isinstance(v, str) and v:
        try:
            return dt.date.fromisoformat(v[:10])
        except ValueError:
            return None
    return None


def _fmt(d: dt.date | None) -> str:
    return d.strftime("%Y.%m.%d") if d else "—"


def _load_episodes(slug: str) -> list[dict]:
    eps = []
    for p in sorted((DATA / slug / "episodes").glob("ep*.md")):
        body, meta = get_data(p.read_text(encoding="utf-8"))
        n = int(meta.get("n") or p.stem[2:])
        st = meta.get("status") or "준비 중"
        eps.append({
            "n": n,
            "id": f"ep{n:02d}",
            "title": meta.get("title", f"{n}화"),
            "short": meta.get("short") or meta.get("title", ""),
            "summary": meta.get("summary", ""),
            "tags": list(meta.get("tags") or []),
            "code_tag": meta.get("code_tag") or f"ep{n:02d}",
            "status": st,
            "status_key": EP_STATUS.get(st, "todo"),
            "video": meta.get("video") or "",
            "length": meta.get("length") or "",
            "doc": meta.get("doc") or "",
            "parent": meta.get("parent") or slug,
            "ai_first": meta.get("ai_first") or "",
            "ai_changed": meta.get("ai_changed") or "",
            "map_ids": [str(x) for x in (meta.get("map") or [])],
            "body": body,
        })
    eps.sort(key=lambda e: e["n"])
    return eps


EX_KIND = {"ex": ("lab", "예제")}


def _load_examples() -> list[dict]:
    """data/examples/envNN.md = 개발 환경 설치, exNN.md = 실습 예제"""
    exs = []
    for prefix, (kind, word) in EX_KIND.items():
        for p in sorted((DATA / "examples").glob(f"{prefix}[0-9]*.md")):
            body, meta = get_data(p.read_text(encoding="utf-8"))
            n = int(meta.get("n") or re.sub(r"\D", "", p.stem) or 0)
            st = meta.get("status") or "준비 중"
            rel = meta.get("related") or {}
            exs.append({
                "n": n,
                "id": f"{prefix}{n:02d}",
                "kind": kind,
                "label": f"{word} {n:02d}",
                "title": meta.get("title", f"{word} {n}"),
                "summary": meta.get("summary", ""),
                "board": meta.get("board", ""),
                "time": meta.get("time", ""),
                "tools": list(meta.get("tools") or []),
                "tags": list(meta.get("tags") or []),
                "dir": meta.get("dir") or "",
                "needs_ids": list(meta.get("needs") or []),
                "status": st,
                "status_key": EX_STATUS.get(st, "todo"),
                "video": meta.get("video") or "",
                "related_slug": rel.get("project") or "",
                "related_ep": rel.get("ep"),
                "map_ids": [str(x) for x in (meta.get("map") or [])],
                "body": body,
            })
    for kind in ("setup", "lab"):
        group = sorted([x for x in exs if x["kind"] == kind], key=lambda e: e["n"])
        for i, x in enumerate(group):
            x["prev"] = group[i - 1] if i > 0 else None
            x["next"] = group[i + 1] if i + 1 < len(group) else None
    exs.sort(key=lambda e: (e["kind"] != "setup", e["n"]))
    return exs


def _load_setup() -> list[dict]:
    """data/setup/_toc.yml 이 목차, data/setup/<slug>.md 가 본문. 파일이 없으면 '준비 중'으로만 보여요."""
    toc = _yaml(DATA / "setup" / "_toc.yml", [])
    groups = []
    for gi, g in enumerate(toc, 1):
        items = []
        for ii, it in enumerate(g.get("items") or [], 1):
            it = {"slug": it} if isinstance(it, str) else dict(it)
            path = DATA / "setup" / f"{it['slug']}.md"
            body, meta = get_data(path.read_text(encoding="utf-8")) if path.exists() else ("", {})
            st = meta.get("status") or ("준비 중" if path.exists() else "계획")
            items.append({
                "slug": it["slug"],
                "num": f"{gi}-{ii}",
                "title": meta.get("title") or it.get("title") or it["slug"],
                "summary": meta.get("summary") or it.get("summary", ""),
                "time": meta.get("time", ""),
                "tools": list(meta.get("tools") or []),
                "tags": list(meta.get("tags") or []),
                "video": meta.get("video") or "",
                "status": st,
                "status_key": EX_STATUS.get(st, "todo"),
                "has_page": path.exists(),
                "needs_ids": list(meta.get("needs") or []),
                "group": g.get("label", ""),
                "body": body,
            })
        groups.append({"num": gi, "label": g.get("label", ""), "desc": g.get("desc", ""), "items": items})
    flat = [x for g in groups for x in g["items"] if x["has_page"]]
    by = {x["slug"]: x for g in groups for x in g["items"]}
    for i, x in enumerate(flat):
        x["prev"] = flat[i - 1] if i > 0 else None
        x["next"] = flat[i + 1] if i + 1 < len(flat) else None
    for x in by.values():
        x["needs"] = [by[n] for n in x["needs_ids"] if n in by]
    return groups


MAP_LEVEL = {"core": "직접 다룸", "part": "일부", "none": "다루지 않음"}


PRI = [("req", "필수", "Required"), ("rec", "권장", "Recommended"), ("opt", "선택", "Optional")]
PRI_KO = dict((k, ko) for k, ko, _ in PRI)
REF_ORDER = {"ep": 0, "ex": 1, "setup": 2}


def _mslug(s) -> str:
    """지도 칸 주소를 만드는 규칙. C++ → cpp · C# → csharp · 'JTAG / SWD' → jtag-swd"""
    s = str(s or "").strip().lower().replace("++", "pp").replace("#", "sharp")
    return re.sub(r"[^a-z0-9가-힣]+", "-", s).strip("-")


def _build_map(projects, examples, setups) -> dict:
    """로드맵 지도. 연결은 두 방향으로 적을 수 있어요.

    1. data/map.yml 의 칸에  links: [ep:<프로젝트>:<회차>, ex:exNN, setup:<slug>]
    2. 회차 · 예제 파일 머리말에  map: [<칸 주소>, ...]   ← 영상 찍고 이쪽만 고치면 돼요

    칸 주소는 `<그룹>.<영문 이름 slug>` 예: lang.c · fund.memory-management.
    map.yml 의 칸에 id: 를 직접 적으면 그게 주소가 돼요. 머리말에는 앞의 그룹을
    빼고 뒷부분만 (memory-management) 적어도 되고, 한글 이름으로도 찾아요.
    못 찾거나 여러 칸에 맞으면 빌드할 때 경고가 떠요.
    """
    m = _yaml(DATA / "map.yml", {})
    if not m:
        return {}

    # 1) 칸마다 주소를 붙인다
    allitems = []
    for gid, g in (m.get("groups") or {}).items():
        g["id"] = gid
        for it in g.get("items") or []:
            it["gid"] = gid
            it["g_ko"] = g.get("ko") or g.get("en") or gid
            it["g_en"] = g.get("en") or gid
            it["id"] = it.get("id") or f"{gid}.{_mslug(it.get('en') or it.get('ko'))}"
            it["p_ko"] = PRI_KO.get(it.get("p"), "")
            it["refs"] = []
            allitems.append(it)

    by_id: dict[str, dict] = {}
    for it in allitems:
        if it["id"] in by_id:
            log.warning("map.yml: 칸 주소가 겹쳐요 — %r. 한쪽 항목에 id: 를 직접 적어 주세요.", it["id"])
        by_id[it["id"]] = it

    def find(key):
        """머리말의 map: 값으로 칸을 찾아요. 전체 주소 · 뒷부분 · 한글/영문 이름 다 됩니다."""
        k = str(key or "").strip()
        if k in by_id:
            return by_id[k], ""
        s = _mslug(k)
        if s in by_id:
            return by_id[s], ""
        for pool in ([it for it in allitems if it["id"].partition(".")[2] == s],
                     [it for it in allitems if s in (_mslug(it.get("ko")), _mslug(it.get("en")))]):
            if len(pool) == 1:
                return pool[0], ""
            if pool:
                return None, "여러 칸에 맞아요 — 앞에 그룹까지 붙여 주세요: " + " · ".join(x["id"] for x in pool)
        return None, "그런 칸이 없어요"

    def mkref(label, title, url, kind, obj):
        return {"label": label, "title": title, "url": url, "kind": kind,
                "on": obj["status_key"] == "on", "status": obj.get("status") or "",
                "skey": obj["status_key"], "n": obj.get("n") or 0}

    # 2) map.yml 의 links: — 칸에서 회차로
    def ref(raw: str):
        kind, _, rest = raw.partition(":")
        if kind == "ep":
            slug, _, n = rest.rpartition(":")
            p = next((x for x in projects if x["slug"] == slug), None)
            if not p:
                return None, f"프로젝트 {slug!r} 가 projects.yml 에 없어요"
            if not n.isdigit():
                return None, "회차 번호가 숫자가 아니에요 (ep:<프로젝트>:<번호>)"
            e = next((x for x in p["eps"] if x["n"] == int(n)), None)
            if not e:
                return None, f"{slug} 에 {n}화가 없어요"
            return mkref(f"{e['n']}화", e["title"], f"projects/{slug}/{e['id']}/", "ep", e), ""
        if kind == "ex":
            x = next((x for x in examples if x["id"] == rest), None)
            if not x:
                return None, f"예제 {rest!r} 가 data/examples/ 에 없어요"
            return mkref(x["label"], x["title"], f"examples/{x['id']}/", "ex", x), ""
        if kind == "setup":
            x = setups.get(rest)
            if not x:
                return None, f"개발 환경 {rest!r} 가 data/setup/_toc.yml 에 없어요"
            if not x["has_page"]:
                return None, ""  # 아직 글이 없는 항목은 조용히 넘어가요
            return mkref(x["num"], x["title"], f"setup/{x['slug']}/", "setup", x), ""
        return None, "ep: · ex: · setup: 중 하나로 시작해 주세요"

    for it in allitems:
        for raw in it.get("links") or []:
            r, why = ref(str(raw))
            if r:
                it["refs"].append(r)
            elif why:
                log.warning("map.yml: 칸 %s 의 연결 %r — %s", it["id"], raw, why)

    # 3) 회차 · 예제 머리말의 map: — 회차에서 칸으로
    sources = [(e, f"projects/{p['slug']}/{e['id']}/", f"{e['n']}화", "ep", f"{p['slug']} {e['n']}화")
               for p in projects for e in p["eps"]]
    sources += [(x, f"examples/{x['id']}/", x["label"], "ex", x["label"]) for x in examples]
    for obj, url, label, kind, where in sources:
        obj["map_items"] = []
        for raw in obj.get("map_ids") or []:
            it, why = find(raw)
            if not it:
                log.warning("%s 의 map: %r — %s", where, raw, why)
                continue
            if not any(r["url"] == url for r in it["refs"]):
                it["refs"].append(mkref(label, obj["title"], url, kind, obj))
            obj["map_items"].append({"id": it["id"], "ko": it.get("ko") or it.get("en"),
                                     "en": it.get("en") or "", "p": it.get("p"),
                                     "p_ko": it["p_ko"], "g_ko": it["g_ko"], "g_en": it["g_en"]})

    # 4) 칸마다 상태를 센다. '예정'과 '영상 공개됨'을 따로 셉니다.
    counts = {"all": 0, "now": 0, "proj": 0, "on": 0, "gap": 0}
    for it in allitems:
        it["refs"].sort(key=lambda r: (REF_ORDER.get(r["kind"], 9), r["n"]))
        it["n_refs"] = len(it["refs"])
        it["n_on"] = sum(1 for r in it["refs"] if r["on"])
        it["proj"] = bool(it["refs"])
        it["done"] = it["n_on"] > 0
        it["now"] = bool(it.get("now"))
        it["tip"] = " · ".join(f"{r['label']} {r['title']}" for r in it["refs"])
        it["gap"] = it.get("p") in ("req", "rec") and not it["now"] and not it["proj"]
        counts["all"] += 1
        counts["now"] += it["now"]
        counts["proj"] += it["proj"]
        counts["on"] += it["done"]
        counts["gap"] += it["gap"]
    m["counts"] = counts
    m["proj_items"] = sorted([it for it in allitems if it["proj"]],
                             key=lambda it: (not it["done"], it["gid"], it["id"]))
    m["coverage"] = []
    for key, ko, en in PRI:
        xs = [it for it in allitems if it.get("p") == key]
        n_on = sum(1 for it in xs if it["done"])
        n_plan = sum(1 for it in xs if (it["proj"] or it["now"]) and not it["done"])
        n = len(xs)
        m["coverage"].append({
            "key": key, "ko": ko, "en": en, "total": n,
            "on": n_on, "planned": n_plan, "done": n_on + n_plan,
            "pct_on": round(100 * n_on / n) if n else 0,
            "pct_plan": round(100 * n_plan / n) if n else 0,
            "pct": round(100 * (n_on + n_plan) / n) if n else 0,
            "next": [it for it in xs if it["gap"]],
        })
    return m


def _load_posts(docs_dir: Path) -> list[dict]:
    posts = []
    for p in sorted((docs_dir / "blog" / "posts").glob("*.md")):
        body, meta = get_data(p.read_text(encoding="utf-8"))
        d = _date(meta.get("date"))
        slug = meta.get("slug") or p.stem
        excerpt = meta.get("description")
        if not excerpt:
            lines = [l.strip() for l in body.split("<!-- more -->")[0].splitlines()
                     if l.strip() and not l.startswith("#")]
            excerpt = lines[0] if lines else ""
        posts.append({
            "title": meta.get("title") or p.stem,
            "date": d,
            "date_str": _fmt(d),
            "url": f"blog/{d:%Y/%m/%d}/{slug}/" if d else "blog/",
            "excerpt": excerpt,
            "tags": list(meta.get("tags") or []),
            "project": meta.get("project") or "",
            "category": meta.get("category") or "기록",
            "src": p.name,
        })
    posts.sort(key=lambda x: x["date"] or dt.date.min, reverse=True)
    for i, x in enumerate(posts):  # 최신순: 앞이 다음(새 글), 뒤가 이전(옛 글)
        x["newer"] = posts[i - 1] if i > 0 else None
        x["older"] = posts[i + 1] if i + 1 < len(posts) else None
    return posts


def _build(config) -> dict:
    extra = config.get("extra") or {}
    user = extra.get("github_user") or ""
    projects = _yaml(ROOT / "projects.yml", [])
    groups = _yaml(DATA / "tags.yml", [])
    posts = _load_posts(Path(config["docs_dir"]))
    examples = _load_examples()
    setup_groups = _load_setup()
    setups = {x["slug"]: x for g in setup_groups for x in g["items"]}
    for x in examples:
        x["needs"] = [setups[n] for n in x["needs_ids"] if n in setups]

    all_parts: dict[str, dict] = {}
    for p in projects:
        slug = p["slug"]
        p["status"] = p.get("status") or "준비 중"
        p["status_key"] = PROJ_STATUS.get(p["status"], "todo")
        p["kind"] = p.get("kind") if p.get("kind") in KIND else "main"
        p["kind_label"] = KIND[p["kind"]]
        p["tags"] = list(p.get("tags") or [t for g in p.get("tech") or [] for t in g.get("items", [])])
        p["tech"] = p.get("tech") or []
        p["updated_str"] = _fmt(_date(p.get("updated")))
        p["repo_url"] = f"https://github.com/{user}/{p['repo']}" if p.get("repo") and user else ""
        p["eps"] = _load_episodes(slug)
        p["ep_on"] = sum(1 for e in p["eps"] if e["status_key"] == "on")
        p["posts"] = [x for x in posts if x["project"] == slug]
        parts = _yaml(DATA / slug / "parts.yml", [])
        cats: list[str] = []
        for it in parts:
            it["status"] = it.get("status") or "나중"
            it["status_key"] = PART_STATUS.get(it["status"], "later")
            it.setdefault("buy", "")
            it.setdefault("doc", "")
            q = it.get("qty")
            it["qty_str"] = f"×{q}" if isinstance(q, int) else (str(q) if q else "")
            if it["cat"] not in cats:
                cats.append(it["cat"])
            g = all_parts.setdefault(it["name"], {**it, "used": []})
            g["used"].append({"slug": slug, "name": p["name"], "qty": it["qty_str"]})
        p["parts"] = parts
        p["part_groups"] = [{"label": c, "items": [x for x in parts if x["cat"] == c]} for c in _cat_sort(cats)]
        p["parts_summary"] = f"{len(parts)}종 · " + " · ".join(
            f"{s} {sum(1 for x in parts if x['status'] == s)}" for s in PART_STATUS_ORDER)

    # 태그: 영상(회차) · 글 · 프로젝트
    def tag_entry(name: str, label: str) -> dict:
        videos = [{"project": p, "ep": e} for p in projects for e in p["eps"] if name in e["tags"]]
        tposts = [x for x in posts if name in x["tags"]]
        tprojects = [p for p in projects if name in p["tags"]]
        texs = [x for x in examples if name in x["tags"]]
        tsets = [x for x in setups.values() if x["has_page"] and name in x["tags"]]
        return {"name": name, "group": label, "videos": videos, "posts": tposts,
                "projects": tprojects, "examples": texs, "setups": tsets,
                "count": len(videos) + len(tposts) + len(tprojects) + len(texs) + len(tsets)}

    tags = [tag_entry(n, g["label"]) for g in groups for n in g.get("items", [])]

    cats_all: list[str] = []
    for it in all_parts.values():
        if it["cat"] not in cats_all:
            cats_all.append(it["cat"])
    parts_all = list(all_parts.values())

    # 예제 ↔ 메인 프로젝트 회차 연결
    for x in examples:
        rp = next((p for p in projects if p["slug"] == x["related_slug"]), None)
        x["related_project"] = rp
        x["related_ep_obj"] = next((e for e in rp["eps"] if e["n"] == x["related_ep"]), None) if rp else None
    for p in projects:
        for e in p["eps"]:
            e["examples"] = [x for x in examples if x["related_project"] is p and x["related_ep"] == e["n"]]

    # 홈 대표 카드: featured: true 가 있으면 그것, 없으면 첫 번째 진행 중 메인 프로젝트 (1개)
    featured = [p for p in projects if p.get("featured")][:1] or \
        [p for p in projects if p["status_key"] == "wip" and p["kind"] == "main"][:1]
    for p in projects:
        p["proj_posts"] = p["posts"]
    for x in posts:
        x["project_obj"] = next((p for p in projects if p["slug"] == x["project"]), None)
    post_cats = []
    for x in posts:
        if x["category"] not in post_cats:
            post_cats.append(x["category"])
    post_cats = [{"label": c, "count": sum(1 for x in posts if x["category"] == c)} for c in post_cats]

    return {
        "user": user,
        "youtube": extra.get("youtube") or "",
        "email": extra.get("email") or "",
        "projects": projects,
        "featured": featured,
        "others": [p for p in projects if p not in featured],
        "post_cats": post_cats,
        "counts": {k: sum(1 for p in projects if p["status_key"] == k) for k in ("wip", "todo", "done")},
        "kind_counts": {k: sum(1 for p in projects if p["kind"] == k) for k in KIND},
        "examples": examples,
        "setup_groups": setup_groups,
        "map": _build_map(projects, examples, setups),
        "setup_count": sum(1 for x in setups.values() if x["has_page"]),
        "groups": groups,
        "posts": posts,
        "tags": tags,
        "parts": parts_all,
        "part_cats": [{"label": c, "items": [x for x in parts_all if x["cat"] == c]} for c in _cat_sort(cats_all)],
        "part_status": [{"label": s, "key": PART_STATUS[s],
                         "count": sum(1 for x in parts_all if x["status"] == s)} for s in PART_STATUS_ORDER],
    }


def on_config(config):
    HB.clear()
    HB.update(_build(config))
    return config


def _page(config, uri: str, meta: dict, body: str = "") -> File:
    fm = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False)
    return File.generated(config, uri, content=f"---\n{fm}---\n{body}")


def on_files(files, config):
    hide = ["toc"]  # 왼쪽 메뉴는 CSS로 큰 화면에서만 숨김 (휴대폰 메뉴 유지)
    files.append(_page(config, "projects/index.md",
                       {"title": "모든 프로젝트", "template": "projects.html", "hide": hide}))
    files.append(_page(config, "tags/index.md",
                       {"title": "다루는 것", "template": "tags.html", "hide": hide}))
    files.append(_page(config, "parts/index.md",
                       {"title": "부품", "template": "parts.html", "hide": hide}))
    files.append(_page(config, "examples/index.md",
                       {"title": "예제", "template": "examples.html", "hide": hide}))
    if HB.get("map"):
        files.append(_page(config, "map/index.md",
                           {"title": "다루는 영역", "template": "map.html", "hide": hide}))
    files.append(_page(config, "setup/index.md",
                       {"title": "개발 환경", "template": "setup.html", "hide": hide}))
    for g in HB["setup_groups"]:
        for x in g["items"]:
            if x["has_page"]:
                files.append(_page(config, f"setup/{x['slug']}.md",
                                   {"title": x["title"], "template": "setup-page.html",
                                    "hide": hide, "hb_setup": x["slug"]}, x["body"]))
    for x in HB["examples"]:
        files.append(_page(config, f"examples/{x['id']}.md",
                           {"title": f"{x['label']} {x['title']}", "template": "example.html",
                            "hide": hide, "hb_ex": x["id"]}, x["body"]))
    for p in HB["projects"]:
        if not p.get("eps") and not p.get("parts") and not p.get("repo"):
            continue  # 자리만 잡아 둔 프로젝트는 상세 페이지를 만들지 않아요
        p["has_page"] = True
        files.append(_page(config, f"projects/{p['slug']}/index.md",
                           {"title": p["name"], "template": "project.html", "hide": hide,
                            "hb_slug": p["slug"]}))
        for e in p["eps"]:
            files.append(_page(config, f"projects/{p['slug']}/{e['id']}.md",
                               {"title": f"{e['n']}화 {e['title']}", "template": "episode.html",
                                "hide": hide, "hb_slug": p["slug"], "hb_ep": e["n"]},
                               e["body"]))
    return files


def on_page_context(context, page, config, nav):
    context["hb"] = HB
    src = Path(page.file.src_uri).name if page.file else ""
    if page.file and page.file.src_uri.startswith("blog/posts/"):
        context["hb_post"] = next((x for x in HB["posts"] if x["src"] == src), None)
    su = page.meta.get("hb_setup")
    if su:
        context["hb_s"] = next(x for g in HB["setup_groups"] for x in g["items"] if x["slug"] == su)
    xn = page.meta.get("hb_ex")
    if xn:
        context["hb_x"] = next(x for x in HB["examples"] if x["id"] == xn)
    slug = page.meta.get("hb_slug")
    if slug:
        proj = next(p for p in HB["projects"] if p["slug"] == slug)
        context["hb_project"] = proj
        n = page.meta.get("hb_ep")
        if n:
            i = next(k for k, e in enumerate(proj["eps"]) if e["n"] == n)
            context["hb_ep"] = proj["eps"][i]
            context["hb_prev"] = proj["eps"][i - 1] if i > 0 else None
            context["hb_next"] = proj["eps"][i + 1] if i + 1 < len(proj["eps"]) else None
    return context


_IMG = re.compile(r"<img(?![^>]*\bloading=)")


def on_page_content(html, page, config, files):
    """본문 사진은 화면에 가까워질 때만 내려받게(lazy) 해요."""
    return _IMG.sub('<img loading="lazy" decoding="async"', html)
