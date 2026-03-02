from playwright.sync_api import sync_playwright
import re
import time
from typing import List, Tuple, Optional, Dict, Set

URL = "file:///C:/Users/kjohn/OneDrive/Desktop/prograrmming-ws/msp-ws/index.html"
TYPE_RE = re.compile(r"hd_type([1-8])")

# 상태 표현
# -1: 닫힘(미확정)
# -2: 깃발(지뢰로 확정 표시)
#  0~8: 열린 숫자(0 포함)
UNKNOWN_CLOSED = -1
FLAGGED_MINE = -2


def parse_cell_state(class_name: str) -> Optional[int]:
    """
    returns:
      UNKNOWN_CLOSED(-1), FLAGGED_MINE(-2), 0..8
      None: 알 수 없는 상태(예: 게임오버 특수 표시 등)
    """
    cls = class_name.split()

    if "hd_closed" in cls:
        if "hd_flag" in cls:
            return FLAGGED_MINE
        return UNKNOWN_CLOSED

    # 열림 + 숫자
    m = TYPE_RE.search(class_name)
    if m:
        return int(m.group(1))

    # 열렸는데 type이 없으면 보통 0
    if "hd_opened" in cls:
        return 0

    return None


def read_board(page) -> Tuple[List[List[Optional[int]]], int, int]:
    """
    board[y][x] 형태로 반환 (y=row, x=col)
    각 칸 값: -1(닫힘), -2(깃발), 0..8(열림), None(미확인)
    """
    cells = page.eval_on_selector_all(
        "div.cell",
        """els => els.map(e => ({
            x: parseInt(e.dataset.x),
            y: parseInt(e.dataset.y),
            cls: e.className
        }))"""
    )

    max_x = max(c["x"] for c in cells)
    max_y = max(c["y"] for c in cells)
    w, h = max_x + 1, max_y + 1

    board: List[List[Optional[int]]] = [[None for _ in range(w)] for _ in range(h)]
    for c in cells:
        x, y = c["x"], c["y"]
        board[y][x] = parse_cell_state(c["cls"])

    return board, w, h


def neighbors(x: int, y: int, w: int, h: int):
    for ny in range(max(0, y - 1), min(h, y + 2)):
        for nx in range(max(0, x - 1), min(w, x + 2)):
            if nx == x and ny == y:
                continue
            yield nx, ny


def find_deterministic_moves(board: List[List[Optional[int]]], w: int, h: int):
    """
    기본 규칙 + 고급 집합(Subset) 규칙:
      1) 기본: 숫자 주변 깃발/닫힌칸 수 일치 확인
      2) 고급: 인접한 두 숫자의 닫힌칸 집합이 포함 관계일 때 차집합 영역 추론 (1-2-1, 1-1 패턴 등 해결)
    """
    to_reveal: Set[Tuple[int, int]] = set()
    to_flag: Set[Tuple[int, int]] = set()

    # 각 숫자 칸의 정보 미리 수집
    num_cells = []
    for y in range(h):
        for x in range(w):
            v = board[y][x]
            if v is not None and isinstance(v, int) and v > 0:
                n_closed = []
                n_flag = 0
                for nx, ny in neighbors(x, y, w, h):
                    s = board[ny][nx]
                    if s == UNKNOWN_CLOSED:
                        n_closed.append((nx, ny))
                    elif s == FLAGGED_MINE:
                        n_flag += 1
                
                remaining_mines = v - n_flag
                if remaining_mines < 0: continue

                # 기본 규칙 처리
                if remaining_mines == 0 and n_closed:
                    to_reveal.update(n_closed)
                elif remaining_mines == len(n_closed) and n_closed:
                    to_flag.update(n_closed)
                
                # 정보 저장 (고급 규칙용)
                if n_closed:
                    num_cells.append({
                        'pos': (x, y),
                        'val': v,
                        'remaining': remaining_mines,
                        'neighbors': set(n_closed)
                    })

    # 고급 규칙: Subset Analysis (집합 분석)
    # 두 숫자 칸 C1, C2에 대해 Neighbors(C1) ⊂ Neighbors(C2) 인지 확인
    for i in range(len(num_cells)):
        for j in range(len(num_cells)):
            if i == j: continue
            c1 = num_cells[i]
            c2 = num_cells[j]

            # C1의 모든 닫힌 이웃이 C2의 이웃이기도 한 경우
            if c1['neighbors'].issubset(c2['neighbors']):
                extra_neighbors = c2['neighbors'] - c1['neighbors']
                if not extra_neighbors: continue

                extra_mines = c2['remaining'] - c1['remaining']

                # 1) 남은 지뢰 차이가 0이면, 나머지 칸은 모두 안전
                if extra_mines == 0:
                    if not to_reveal.intersection(extra_neighbors):
                        # print(f"[ADVANCED] Subset Safe: Based on {c1['pos']} and {c2['pos']}")
                        to_reveal.update(extra_neighbors)
                
                # 2) 남은 지뢰 차이가 나머지 칸 수와 같으면, 나머지 칸은 모두 지뢰
                elif extra_mines == len(extra_neighbors):
                    if not to_flag.intersection(extra_neighbors):
                        # print(f"[ADVANCED] Subset Mine: Based on {c1['pos']} and {c2['pos']}")
                        to_flag.update(extra_neighbors)

    to_reveal.difference_update(to_flag)
    return to_reveal, to_flag


def find_best_guess(board: List[List[Optional[int]]], w: int, h: int) -> Optional[Tuple[int, int]]:
    """
    확정 지점이 없을 때 확률적으로 가장 안전한 칸을 찾음.
    방법: 각 숫자칸 주변의 (남은 지뢰수 / 닫힌 칸수)를 계산하여 
    인접한 닫힌 칸들에게 할당. 여러 숫자와 인접한 경우 최대 확률(가장 보수적)을 채택.
    최종적으로 그 중 확률이 가장 낮은 칸을 선택.
    """
    cell_probs: Dict[Tuple[int, int], float] = {}
    
    # 모든 숫자 칸을 순회하며 주변 확률 계산
    for y in range(h):
        for x in range(w):
            v = board[y][x]
            # 열린 숫자 칸이고 0보다 큰 경우
            if v is not None and isinstance(v, int) and v > 0:
                n_closed = []
                n_flag = 0
                for nx, ny in neighbors(x, y, w, h):
                    s = board[ny][nx]
                    if s == UNKNOWN_CLOSED:
                        n_closed.append((nx, ny))
                    elif s == FLAGGED_MINE:
                        n_flag += 1
                
                if n_closed:
                    local_prob = (v - n_flag) / len(n_closed)
                    for cx, cy in n_closed:
                        # 한 칸이 여러 숫자와 닿아있으면 가장 높은 위험도를 기록
                        if (cx, cy) not in cell_probs or local_prob > cell_probs[(cx, cy)]:
                            cell_probs[(cx, cy)] = local_prob

    if cell_probs:
        # 확률이 가장 낮은(안전한) 칸 반환
        best_cell = min(cell_probs.keys(), key=lambda c: cell_probs[c])
        print(f"[GUESS] Frontier found. Safest cell: {best_cell} with local risk {cell_probs[best_cell]:.2%}")
        return best_cell

    # 프론티어가 없는 경우 (완전 고립된 칸들만 남음) - 랜덤하게 하나 선택
    all_closed = []
    for y in range(h):
        for x in range(w):
            if board[y][x] == UNKNOWN_CLOSED:
                all_closed.append((x, y))
    
    if all_closed:
        print(f"[GUESS] No frontier. Picking random closed cell: {all_closed[0]}")
        return all_closed[0]

    return None


def left_click(page, x: int, y: int):
    page.click(f"#cell_{x}_{y}", button="left")


def right_click(page, x: int, y: int):
    page.click(f"#cell_{x}_{y}", button="right")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded")

        # 첫 클릭: 보통 첫 클릭 안전 룰이라 (0,0) 추천
        left_click(page, 0, 0)
        time.sleep(0.08)

        # 자동 스텝 루프
        step = 0
        while True:
            # 게임 종료 감지 (승리/패배 배너 확인)
            result = page.inner_text("#result-banner")
            if result:
                print(f"[FINISH] Game Ended: {result}")
                break

            board, w, h = read_board(page)
            to_reveal, to_flag = find_deterministic_moves(board, w, h)

            if not to_reveal and not to_flag:
                # 확정 지점이 없으면 추측 실행
                guess = find_best_guess(board, w, h)
                if guess:
                    left_click(page, guess[0], guess[1])
                    time.sleep(0.1)
                    step += 1
                    continue
                else:
                    print(f"[STOP] No more moves possible at step={step}")
                    break

            # 사람처럼: 깃발 먼저 꽂고 -> 안전칸 열기
            for x, y in sorted(to_flag):
                # 이미 깃발이면 skip
                if board[y][x] != FLAGGED_MINE:
                    right_click(page, x, y)
                    time.sleep(0.01)

            for x, y in sorted(to_reveal):
                # 아직 닫혀있을 때만 클릭
                if board[y][x] == UNKNOWN_CLOSED:
                    left_click(page, x, y)
                    time.sleep(0.01)

            step += 1
            time.sleep(0.05)

        print("Solver finished. Keeping browser open for statistics...")
        # 브라우저가 바로 닫히지 않도록 대기 (사용자가 직접 닫을 때까지)
        page.wait_for_timeout(1000000) 

if __name__ == "__main__":

    START = time.time()
    main()
    END = time.time()
    print(f"END!! {END - START}")