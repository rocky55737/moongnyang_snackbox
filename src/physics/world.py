"""물리 세계: pymunk Space 래퍼. 벽 생성, 충돌 감지, 머지 처리.

머지(병합)는 충돌 콜백 안에서 바로 처리하지 않고 큐에 쌓은 뒤
space.step() 직후에 처리한다 (pymunk는 step 도중 바디 추가/삭제 금지).
"""
import time
import pymunk

from src.config import (
    WIDTH, HEIGHT, WALL, GROUND_TOP, GRAVITY, DANGER_Y,
    COLLTYPE_SNACK, COLLTYPE_WALL, MAX_TIER,
)
from src.factories.snack_factory import SnackFactory
from src.events.event_bus import EventBus
from src.events.events import SnackMerged, BugiCreated, BugiPopped


class PhysicsWorld:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        self.space.damping = 0.85  # 초당 15% 속도 감쇠 → 간식이 빠르게 안정
        self._build_walls()

        self.factory = SnackFactory(self.space)
        self.snacks: set = set()
        self._merge_queue: list = []

        self.space.on_collision(
            COLLTYPE_SNACK, COLLTYPE_SNACK, begin=self._on_snack_collision
        )

    # --- 구성 ---
    def _build_walls(self) -> None:
        static = self.space.static_body
        segments = [
            ((WALL, 0), (WALL, HEIGHT)),                       # 왼쪽
            ((WIDTH - WALL, 0), (WIDTH - WALL, HEIGHT)),       # 오른쪽
            ((WALL, GROUND_TOP), (WIDTH - WALL, GROUND_TOP)),  # 바닥
        ]
        for a, b in segments:
            seg = pymunk.Segment(static, a, b, 4)
            seg.elasticity = 0.0
            seg.friction = 1.0
            seg.collision_type = COLLTYPE_WALL
            self.space.add(seg)

    # --- 생성/삭제 ---
    def spawn(self, tier: int, x: float, y: float):
        snack = self.factory.create(tier, x, y)
        self.snacks.add(snack)
        return snack

    def _remove(self, snack) -> None:
        if snack in self.snacks:
            self.space.remove(snack.body, snack.shape)
            self.snacks.discard(snack)

    def clear(self) -> None:
        for snack in list(self.snacks):
            self._remove(snack)
        self._merge_queue.clear()

    # --- 충돌 -> 머지 큐 ---
    def _on_snack_collision(self, arbiter, space, data):
        a, b = arbiter.shapes
        sa = getattr(a, "snack", None)
        sb = getattr(b, "snack", None)
        if sa is None or sb is None:
            return
        if sa.tier != sb.tier or sa.merging or sb.merging:
            return
        sa.merging = sb.merging = True
        self._merge_queue.append((sa, sb))

    # --- 진행 ---
    def step(self, dt: float, substeps: int = 2) -> None:
        for _ in range(substeps):
            self.space.step(dt / substeps)
        self._resolve_merges()

    def _resolve_merges(self) -> None:
        if not self._merge_queue:
            return
        queue, self._merge_queue = self._merge_queue, []
        for sa, sb in queue:
            if sa not in self.snacks or sb not in self.snacks:
                continue
            x = (sa.position.x + sb.position.x) / 2
            y = (sa.position.y + sb.position.y) / 2
            tier = sa.tier
            self._remove(sa)
            self._remove(sb)
            if tier < MAX_TIER:
                new_snack = self.spawn(tier + 1, x, y)
                new_snack.body.velocity = (0, -90)
                self.bus.publish(SnackMerged(new_snack.tier, x, y))
                if new_snack.tier == MAX_TIER:
                    self.bus.publish(BugiCreated(x, y))
            else:
                # 부기 + 부기 -> 펑!
                self.bus.publish(BugiPopped(x, y))

    # --- 게임오버 판정 ---
    def is_in_danger(self) -> bool:
        now = time.monotonic()
        for snack in self.snacks:
            settled = (now - snack.born > 0.9) and snack.body.velocity.length < 30
            if settled and (snack.position.y - snack.spec.radius < DANGER_Y):
                return True
        return False
