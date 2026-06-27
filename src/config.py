"""게임 전역 설정 및 간식 단계(Tier) 정의.

파이썬에서는 모듈 자체가 단일 인스턴스(싱글턴)처럼 동작하므로,
별도 Singleton 클래스를 만들기보다 모듈 상수 + frozen dataclass로 설정을 표현한다.
"""
from dataclasses import dataclass

# --- 화면/물리 ---
WIDTH, HEIGHT = 400, 580
WALL = 20
GROUND_TOP = HEIGHT - 20
DROP_Y = 48
DANGER_Y = 116
FPS = 60
GRAVITY = 900.0

# --- 충돌 타입 ---
COLLTYPE_SNACK = 1
COLLTYPE_WALL = 2

# --- 색상 ---
BG_TOP = (255, 255, 255)
BG_BOTTOM = (241, 233, 255)
DANGER_COLOR = (255, 111, 139)
LAVENDER = (138, 107, 255)


@dataclass(frozen=True)
class TierSpec:
    """간식 한 단계의 불변 명세."""
    index: int
    name: str
    radius: float
    color: tuple
    ring: tuple
    points: int


# 작은 간식 -> 큰 간식 -> 마스코트 부기
TIERS = [
    TierSpec(0, "초코송이",     18, (202, 162, 122), (169, 121, 79),  0),
    TierSpec(1, "칸쵸",         25, (216, 176, 102), (180, 140, 63),  1),
    TierSpec(2, "두바이초코",   33, (127, 174, 87),  (93, 138, 57),   3),
    TierSpec(3, "과일케이크",   42, (246, 182, 207), (229, 137, 173), 6),
    TierSpec(4, "파파존스피자", 52, (241, 193, 78),  (211, 158, 43),  10),
    TierSpec(5, "모짜인더버거", 63, (231, 166, 75),  (197, 131, 44),  15),
    TierSpec(6, "스테이크",     75, (217, 138, 147), (187, 102, 112), 21),
    TierSpec(7, "부기",         88, (155, 224, 176), (108, 199, 139), 28),
]
MAX_TIER = len(TIERS) - 1

# 떨어지는 간식 분포(작은 쪽 우대)
DROPPABLE = [0, 0, 0, 1, 1, 2, 3]

BUGI_POP_BONUS = 100
