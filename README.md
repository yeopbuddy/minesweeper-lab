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

### 1) 기본 확정 규칙
- 숫자칸 기준, 남은 지뢰 수 = 0 → 인접한 닫힌 칸 전부 오픈
- 숫자칸 기준, 남은 지뢰 수 = 인접 닫힌 칸 수 → 인접 닫힌 칸 전부 깃발

### 2) 고급 규칙: 부분집합(Subset) 추론
- 인접한 두 숫자칸의 닫힌 이웃 집합이 포함관계일 때  
  차집합 영역을 이용해 안전/지뢰를 추가 확정  
  (예: 1-2-1, 1-1 변형 패턴 등)

### 3) 추측 (확정이 끊겼을 때)
- 프론티어에서 `남은 지뢰 수 / 닫힌 칸 수` 계산 후  
  가장 낮은 위험도 선택

⚠️ 확정 규칙과 부분집합 추론이 모두 끝나면  
확률 기반으로 플레이하므로 항상 클리어를 보장하지 않습니다.

## 기본 난이도 변경 방법

`minesweeper.html` 맨 아래에서:

```javascript
initGame('expert');
```

을 아래 중 하나로 변경:

```javascript
initGame('beginner');
initGame('intermediate');
initGame('expert');
```

## 아나콘다(Conda) 환경 셋업

```bash
conda create -n minesweeper-bot python=3.10 -y
conda activate minesweeper-bot

pip install playwright
playwright install
```

## 실행

```bash
python mine-local.py
```

Chromium 창이 열리고 솔버가 자동으로 플레이를 시작합니다.

## 중요 참고 사항 ⚠️

- 본 프로젝트는 로컬 실험/학습 목적입니다.
- 이 솔버를 https://minesweeper.online/ 에서 사용할 경우  
  자동화 감지로 인해 IP Block을 당할 수 있습니다.
- 반드시 로컬 `minesweeper.html` 환경에서만 사용하세요.

## Contribution 🤝

- 새로운 추론 로직 (예: 완전 확률 계산, CSP 기반 풀이 등)
- 더 정교한 Guess 전략
- 성능 최적화
- UI 개선
- 통계/데이터 수집 기능 추가

모든 기여를 환영합니다. PR 및 Issue 자유롭게 남겨주세요.

</details>

---

<details>
<summary><strong>English</strong></summary>

This project consists of a **local Minesweeper web implementation** and a **Python Playwright solver bot** that automatically plays the game.

The solver mimics human-like reasoning using deterministic logic, subset inference, and a simple probability-based fallback strategy.

## Project Structure

- `minesweeper.html` — A solver-friendly local Minesweeper implementation
- `mine-local.py` — Playwright-based automated solver

## How It Works (DOM Contract)

The solver reconstructs the board state by reading DOM elements:

- Cell id: `cell_{x}_{y}`
- Attributes: `data-x`, `data-y`
- State classes:
  - `hd_closed`  → hidden cell
  - `hd_opened`  → revealed cell
  - `hd_flag`    → flagged cell
  - `hd_type1..8` → revealed number (1–8)

## Solving Logic

### 1) Deterministic Rules
- If remaining mines = 0 → reveal all adjacent hidden cells
- If remaining mines = number of adjacent hidden cells → flag them all

### 2) Subset Inference (Advanced Rule)
- If the hidden-neighbor set of one number is a subset of another,
  the difference set can be inferred as either safe or mines  
  (solves patterns such as 1-2-1 and similar configurations)

### 3) Guessing (Fallback Strategy)
- When no deterministic moves remain,
  the solver estimates local risk using:
  
  remaining_mines / hidden_neighbors
  
  and selects the cell with the lowest estimated probability.

⚠️ Once deterministic and subset-based rules are exhausted,
the solver switches to probability-based guessing.
Therefore, a win is **not guaranteed**.

## Changing Default Difficulty

At the bottom of `minesweeper.html`, change:

```javascript
initGame('expert');
```

to one of:

```javascript
initGame('beginner');
initGame('intermediate');
initGame('expert');
```

## Conda Environment Setup

```bash
conda create -n minesweeper-bot python=3.10 -y
conda activate minesweeper-bot

pip install playwright
playwright install
```

## Run

```bash
python mine-local.py
```

A Chromium window will open and the solver will begin playing automatically.

## Important Notes ⚠️

- This project is intended for local experimentation and research.
- Using this solver on third-party websites (e.g., https://minesweeper.online/) may result in IP blocking due to automation detection.
- Please use it only with the provided local `minesweeper.html`.

## Contribution 🤝

Contributions are welcome, including:

- Advanced inference logic (e.g., exact probability computation, CSP-based solving)
- Improved guessing heuristics
- Performance optimization
- UI improvements
- Data logging and statistical analysis features

Feel free to open issues or submit pull requests.

</details>
