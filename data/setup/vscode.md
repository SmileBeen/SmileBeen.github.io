---
title: VS Code 설치와 기본 설정
summary: 문서 · 파이썬 · 사이트 파일을 고치는 편집기 준비, 줄바꿈 경고 없애기
tools: [VS Code]
time: 15분
tags: [VS Code]
status: 촬영 준비
video: ""
---

## 어디에 쓰나
펌웨어 빌드는 CubeIDE로 하고, **사이트 글 · 파이썬 도구 · 설정 파일**은 VS Code로 고쳐요.

## 1. 설치
1. `code.visualstudio.com`에서 Windows용(User Installer)을 받아요.
2. 설치 중 **"PATH에 추가"**와 **"탐색기 메뉴에 Code로 열기"**를 체크해요. 폴더 우클릭으로 바로 열 수 있어요.

## 2. 확장 (왼쪽 블록 아이콘)
| 확장 | 용도 |
|---|---|
| Korean Language Pack | 메뉴 한글 (선택) |
| C/C++ (Microsoft) | 펌웨어 코드 읽을 때 정의로 이동 |
| Python (Microsoft) | 시험 · 자동화 스크립트 |
| YAML (Red Hat) | `projects.yml` 같은 설정 파일 오타 표시 |

## 3. 설정 두 가지
**Ctrl + ,** → 검색창에 입력해요.
- `files.eol` → **\n** 으로. git의 "LF will be replaced by CRLF" 경고가 줄어요.
- `files.autoSave` → **afterDelay**. 저장을 깜빡하지 않게요.

## 4. 터미널
**Ctrl + `** 로 아래 터미널을 열어요. 이 채널의 git 명령은 전부 여기서 쳐요.
