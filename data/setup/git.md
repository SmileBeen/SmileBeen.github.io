---
title: Git 설치와 GitHub 연결
summary: Git 설치, 이름 · 이메일 설정, 레포 하나 만들어 첫 push까지
tools: [Git, GitHub]
time: 20분
tags: [Git]
needs: [vscode]
status: 촬영 준비
video: ""
---

## 1. 설치
1. `git-scm.com`에서 **Git for Windows**를 받아요.
2. 설치 옵션은 대부분 기본값. 두 군데만 바꿔요.
    - 기본 편집기: **Visual Studio Code**
    - 기본 브랜치 이름: **main** (Override 선택)

## 2. 내 정보 설정 (한 번만)
```powershell
git config --global user.name "GitHub아이디"
git config --global user.email "숫자+아이디@users.noreply.github.com"
```
이메일은 GitHub **Settings → Emails**의 **Keep my email addresses private**를 켜면 나오는 주소예요. 개인 메일이 공개 커밋에 남지 않아요.

## 3. 레포 만들고 첫 push
1. GitHub → **New repository** → 이름 입력, Public, 나머지 체크는 비워 두기
2. 내 폴더에서:
```powershell
git init
git add .
git commit -m "첫 업로드"
git branch -M main
git remote add origin https://github.com/아이디/레포.git
git push -u origin main
```
3. 처음 push할 때 뜨는 창에서 **브라우저로 로그인**을 고르면 끝이에요.

## 막히면
- **Repository not found** → GitHub에 레포를 먼저 만들었는지, 이름 철자가 같은지 확인
- **`>>`만 나오고 멈춰요** → 붙여넣기 때 줄이 하나 더 들어간 거예요. 엔터 한 번 더
