# SmileBeen.github.io

개인 허브 사이트 원본. https://SmileBeen.github.io/

## 어디를 고치면 되나
| 바꾸고 싶은 것 | 파일 |
|---|---|
| 내 GitHub 아이디 · 유튜브 · 이메일 | `mkdocs.yml` 의 `extra:` |
| 프로젝트 추가 · 종류(main/side) · 상태 · 대표 태그 | `projects.yml` |
| 회차 (제목 · 상태 · 영상 주소 · 본문) | `data/<slug>/episodes/epNN.md` |
| **이 회차가 지도에서 채우는 칸** | `data/<slug>/episodes/epNN.md` 머리말의 `map: [lang.c, ...]` — 칸 주소는 `/map/` 에서 칸을 누르면 나와요 |
| 개발 환경 목차 · 설치 글 | `data/setup/_toc.yml` (순서) · `data/setup/<slug>.md` (본문) |
| 예제 (짧은 실습) | `data/examples/exNN.md` (코드는 `embedded-examples` 레포) |
| 부품표 (수량 · 상태 · 구매/자료 링크) | `data/<slug>/parts.yml` |
| 홈 "다루는 영역" 지도 (층 · 수준 · 연결 회차 · 직군) | `data/map.yml` |
| 홈 "다루는 것" 기술 묶음 | `data/tags.yml` |
| 블로그 글 | `docs/blog/posts/` (머리말에 `slug`, `tags`, `project` 를 적으면 태그·프로젝트 페이지에 연결돼요) |
| 디자인 | `overrides/*.html`, `docs/stylesheets/extra.css` |

`/projects/`, `/projects/<slug>/`, `/projects/<slug>/epNN/`, `/map/`, `/setup/`, `/examples/`, `/tags/`, `/parts/` 페이지는
`hooks/projects.py` 가 빌드할 때 만들어요. 직접 만들 필요 없어요.

## 내 PC에서 미리 보기
```
pip install -r requirements.txt
mkdocs serve
```
http://127.0.0.1:8000 에서 확인.
