---
title: 사이트 내 PC에서 미리 보기
summary: 글이나 설정을 push하기 전에 내 PC에서 사이트 모습 확인하기
tools: [Python, MkDocs]
time: 10분
tags: [Python]
needs: [python, git]
status: 준비 중
video: ""
---

## 띄우기
```powershell
cd D:\youtube\repos\SmileBeen.github.io
py -m pip install -r requirements.txt
py -m mkdocs serve
```
브라우저에서 `http://127.0.0.1:8000` 을 열면 push하기 전 모습을 볼 수 있어요. 파일을 저장하면 바로 새로고침돼요. 끌 때는 터미널에서 **Ctrl + C**.


## 언제 쓰나
- `projects.yml`, 회차 파일처럼 Pages CMS가 아닌 파일을 직접 고쳤을 때
- 사진이 제대로 들어갔는지 push 전에 확인할 때
