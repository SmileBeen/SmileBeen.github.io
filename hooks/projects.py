"""허브 데이터 훅.

projects.yml, data/tags.yml, data/<slug>/parts.yml, data/<slug>/episodes/*.md,
docs/blog/posts/*.md 를 읽어서

  /projects/                      모든 프로젝트   (overrides/projects.html)
  /projects/<slug>/               프로젝트 상세   (overrides/project.html)
  /projects/<slug>/epNN/          회차            (overrides/episode.html)
  /tags/                          다루는 것       (overrides/tags.html)
  /parts/                         부품 전체 BOM   (overrides/parts.html)

페이지를 빌드할 때 만들고, 모든 템플릿에 `hb` 변수로 데이터를 넘겨요.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import yaml
from mkdocs.structure.files import File
from mkdocs.utils.meta import get_data

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PROJ_STATUS = {"진행 중": "wip", "준비 중": "todo", "완료": "done"}
EP_STATUS = {"공개": "on", "편집 중": "wip", "촬영 준비": "wip", "준비 중": "todo"}
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
            "body": body,
        })
    eps.sort(key=lambda e: e["n"])
    return eps


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

    all_parts: dict[str, dict] = {}
    for p in projects:
        slug = p["slug"]
        p["status"] = p.get("status") or "준비 중"
        p["status_key"] = PROJ_STATUS.get(p["status"], "todo")
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
        return {"name": name, "group": label, "videos": videos, "posts": tposts,
                "projects": tprojects, "count": len(videos) + len(tposts) + len(tprojects)}

    tags = [tag_entry(n, g["label"]) for g in groups for n in g.get("items", [])]

    cats_all: list[str] = []
    for it in all_parts.values():
        if it["cat"] not in cats_all:
            cats_all.append(it["cat"])
    parts_all = list(all_parts.values())

    # 홈 대표 카드: featured: true 가 있으면 그것, 없으면 첫 번째 진행 중 프로젝트 (1개)
    featured = [p for p in projects if p.get("featured")][:1] or \
        [p for p in projects if p["status_key"] == "wip"][:1]
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
    hide = ["navigation", "toc"]
    files.append(_page(config, "projects/index.md",
                       {"title": "모든 프로젝트", "template": "projects.html", "hide": hide}))
    files.append(_page(config, "tags/index.md",
                       {"title": "다루는 것", "template": "tags.html", "hide": hide}))
    files.append(_page(config, "parts/index.md",
                       {"title": "부품", "template": "parts.html", "hide": hide}))
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
