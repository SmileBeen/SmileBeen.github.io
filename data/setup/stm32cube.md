---
title: STM32CubeMX · STM32CubeIDE 설치
summary: 설정 도구와 IDE 설치, 쓰는 보드의 펌웨어 패키지를 미리 받아 두기
tools: [STM32CubeMX, STM32CubeIDE 2.x]
time: 40~60분 (다운로드 포함)
tags: [STM32CubeMX, STM32CubeIDE, STM32]
status: 촬영 준비
video: ""
---

## 왜 두 개를 까나
CubeIDE 2.0부터 설정 화면(CubeMX)이 IDE에서 빠졌어요. **CubeMX로 핀 · 클록을 설정하고 코드를 만든 뒤, CubeIDE로 빌드 · 굽기 · 디버깅**해요.

## 1. 받기
1. ST 홈페이지에서 `STM32CubeMX`, `STM32CubeIDE`를 검색해 Windows용을 받아요.
2. 다운로드하려면 ST 계정이 필요해요. 처음이면 가입부터 해요.

## 2. 설치
1. **CubeIDE**를 먼저 설치해요. 중간에 **ST-LINK 드라이버** 설치를 묻는 창이 뜨면 모두 체크해요. 보드를 USB로 연결했을 때 인식시키는 드라이버예요.
2. **CubeMX**를 설치해요. 기본값 그대로 Next.
3. 둘 다 설치 경로에 한글이 없게 해요. (기본 경로 그대로면 괜찮아요)

## 3. 보드 펌웨어 패키지 미리 받기 (시간 제일 오래 걸려요)
첫 프로젝트를 만들 때 자동으로 받기도 하지만, 몇백 MB라 한 번에 받아 두는 게 편해요.

1. CubeMX → **Help → Manage embedded software packages**
2. 이 채널에서 쓰는 보드 시리즈를 체크하고 **Install**
    - STM32G4 (NUCLEO-G474RE)
    - STM32H7 (STM32H743I-EVAL)
    - STM32F7 (STM32F746G-DISCO)
    - STM32F1 (NUCLEO-F103RB)

## 4. 확인
- 보드를 USB로 연결 → 장치 관리자에 **STLink** 장치와 **COM 포트**가 보이면 끝이에요.
- CubeIDE 첫 실행 때 묻는 **Workspace** 폴더는 `D:\youtube\workspace`처럼 한글 없는 곳으로 정해요.

## 막히면
- **다운로드 버튼이 안 눌려요** → ST 계정 로그인 상태인지 확인
- **보드가 안 잡혀요** → 데이터 되는 USB 케이블인지, 드라이버를 설치했는지 확인
