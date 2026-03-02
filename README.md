# Minesweeper Lab (Local) 🧨🤖

<details open>
<summary><strong>한국어</strong></summary>

로컬에서 실행되는 **지뢰찾기 웹 페이지**와, 이를 자동으로 플레이하는 **Python Playwright 솔버 봇**입니다.  
확정 규칙(Deterministic) + 부분집합(Subset) 추론 + 간단한 위험도(확률) 기반 추측을 통해 사람처럼 풀이를 진행합니다.

## 구성
- `minesweeper.html` — 솔버가 읽기 쉬운 DOM 구조로 만든 로컬 지뢰찾기
- `mine-local.py` — Playwright 기반 자동 솔버/봇

## 동작 방식 (DOM 계약)
솔버는 DOM에서 각 셀을 읽어 보드 상태를 복원합니다.

- 셀 id: `cell_{x}_{y}`
- 속성: `data-x`, `data-y`
- 상태 class:
  - `hd_closed` : 닫힘(미오픈)
  - `hd_opened` : 열림(오픈)
  - `hd_flag` : 깃발
  - `hd_type1..8` : 숫자(1~8)

## 풀이 로직
1) **기본 확정 규칙**
- 숫자칸 기준, 남은 지뢰 수 = 0 → 인접한 닫힌 칸 전부 **오픈**
- 숫자칸 기준, 남은 지뢰 수 = 인접 닫힌 칸 수 → 인접 닫힌 칸 전부 **깃발**

2) **고급 규칙: 부분집합(Subset) 추론**
- 인접한 두 숫자칸의 “닫힌 이웃 집합”이 포함관계일 때,
  차집합 영역을 이용해 안전/지뢰를 추가로 확정 (예: 1-2-1, 1-1 변형 패턴 등)

3) **추측(확정이 끊겼을 때)**
- 프론티어(숫자칸과 인접한 닫힌 칸)에서 간단한 지역 위험도  
  `남은 지뢰 수 / 닫힌 칸 수` 를 계산해 가장 낮은 위험도의 칸을 선택

## 요구 사항
- Python 3.10+
- Playwright

## 설치
```bash
pip install playwright
playwright install
```

## 실행
1) `minesweeper.html`과 `mine-local.py`를 같은 폴더에 둡니다.

2) `mine-local.py`에서 로컬 파일 URL을 필요 시 수정합니다.
```py
URL = "file:///C:/path/to/minesweeper.html"
```

3) 실행:
```bash
python mine-local.py
```

Chromium 창이 열리고 솔버가 자동으로 플레이를 시작합니다.

## 참고
- 본 프로젝트는 **로컬 실험/학습/연구 목적**입니다.
- 외부 서비스/웹사이트에 대한 자동화는 해당 사이트 정책을 반드시 준수해 주세요.

</details>

---

<details>
<summary><strong>English</strong></summary>

A local **Minesweeper web page** plus a **Python Playwright solver bot** that plays it automatically.  
It uses deterministic rules, subset inference, and a simple probability-based guessing fallback.

## Contents
- `minesweeper.html` — Local Minesweeper (solver-friendly DOM)
- `mine-local.py` — Playwright solver/bot

## How it works (DOM contract)
- Cell id: `cell_{x}_{y}`
- Attributes: `data-x`, `data-y`
- State classes:
  - `hd_closed` : hidden
  - `hd_opened` : opened
  - `hd_flag` : flagged
  - `hd_type1..8` : opened number (1–8)

## Solving logic
1) Deterministic rules  
2) Subset inference (set containment / difference)  
3) Guessing fallback (simple local risk heuristic)

## Requirements
- Python 3.10+
- Playwright

## Setup
```bash
pip install playwright
playwright install
```

## Run
1) Keep `minesweeper.html` and `mine-local.py` in the same folder.

2) Update the local file URL in `mine-local.py` if needed:
```py
URL = "file:///C:/path/to/minesweeper.html"
```

3) Run:
```bash
python mine-local.py
```

</details>
