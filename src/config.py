"""게임 전역 설정 및 간식 단계(Tier) 정의."""
from dataclasses import dataclass

# --- 화면/물리 ---
WIDTH, HEIGHT = 400, 580
WALL = 20
GROUND_TOP = HEIGHT - 20
DROP_Y = 48
DANGER_Y = 116
FPS = 60
GRAVITY = 900.0

# --- 하단 순서표 ---
CHART_H = 32
WINDOW_HEIGHT = HEIGHT + CHART_H

# --- 충돌 타입 ---
COLLTYPE_SNACK = 1
COLLTYPE_WALL = 2

# --- 색상 ---
BG_TOP = (255, 255, 255)
BG_BOTTOM = (241, 233, 255)
DANGER_COLOR = (255, 111, 139)
LAVENDER = (138, 107, 255)
CHART_BG = (30, 22, 60)


@dataclass(frozen=True)
class TierSpec:
    """간식 한 단계의 불변 명세."""
    index: int
    name: str
    radius: float
    points: int


# 체리 -> 옥수수 -> 아웃백 감자 -> 두쫀쿠 -> 닥터페퍼
# -> 후라이드 치킨 -> 고기 -> 키리쉬 케이크 -> 햄버거 -> 포테이토 피자 -> 낙곱새
TIERS = [
    TierSpec(0,  "체리",          16,  0),
    TierSpec(1,  "옥수수",        20,  1),
    TierSpec(2,  "아웃백 감자",   24,  3),
    TierSpec(3,  "두쫀쿠",        30,  6),
    TierSpec(4,  "닥터페퍼",      37, 10),
    TierSpec(5,  "후라이드 치킨", 46, 15),
    TierSpec(6,  "고기",          57, 21),
    TierSpec(7,  "키리쉬 케이크", 70, 28),
    TierSpec(8,  "햄버거",        87, 36),
    TierSpec(9,  "포테이토 피자", 107, 45),
    TierSpec(10, "낙곱새",        132, 55),
]
MAX_TIER = len(TIERS) - 1

# 떨어지는 간식 분포 (작은 쪽 우대)
DROPPABLE = [0, 0, 0, 1, 1, 2, 3]

BUGI_POP_BONUS = 100
