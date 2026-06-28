"""SnackFactory: 단계별 물리 속성을 캡슐화해 Snack을 생성한다 (Factory 패턴).

생성 로직을 한 곳에 모아, 나머지 코드는 'tier와 좌표'만 알면 되도록 한다.
"""
import time
import pymunk

from src.config import TIERS, COLLTYPE_SNACK
from src.entities.snack import Snack


class SnackFactory:
    def __init__(self, space: pymunk.Space) -> None:
        self.space = space

    def create(self, tier: int, x: float, y: float) -> Snack:
        spec = TIERS[tier]
        # 선형 질량: 반지름 제곱 대신 선형 비례 → 큰 간식이 작은 것을 날리는 현상 완화
        mass = spec.radius * 0.04
        moment = pymunk.moment_for_circle(mass, 0, spec.radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)

        shape = pymunk.Circle(body, spec.radius)
        shape.elasticity = 0.0   # 탄성 제거 → 통통 튀지 않음
        shape.friction = 1.0     # 최대 마찰 → 바닥/벽 접촉 시 즉시 제동
        shape.collision_type = COLLTYPE_SNACK

        snack = Snack(tier, body, shape, time.monotonic())
        shape.snack = snack  # 충돌 콜백에서 역참조용
        self.space.add(body, shape)
        return snack
