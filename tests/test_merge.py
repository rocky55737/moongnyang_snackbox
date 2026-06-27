"""코어 물리/이벤트 로직 헤드리스 테스트 (pygame 불필요)."""
from src.events.event_bus import EventBus
from src.events.events import SnackMerged
from src.physics.world import PhysicsWorld
from src.systems.score import ScoreSystem
from src.config import WIDTH, MAX_TIER


def _step_until(world, cond, max_steps=900, dt=1 / 60):
    for _ in range(max_steps):
        world.step(dt)
        if cond():
            return True
    return False


def test_two_same_tier_merge_into_next():
    bus = EventBus()
    world = PhysicsWorld(bus)
    score = ScoreSystem(bus)
    x = WIDTH / 2
    world.spawn(0, x - 6, 300)
    world.spawn(0, x + 6, 300)
    merged = _step_until(world, lambda: any(s.tier == 1 for s in world.snacks))
    assert merged, "같은 단계 간식 두 개는 다음 단계로 합쳐져야 한다"
    assert score.score >= 1


def test_merge_publishes_event():
    bus = EventBus()
    world = PhysicsWorld(bus)
    received = []
    bus.subscribe(SnackMerged, received.append)
    world.spawn(0, 200, 300)
    world.spawn(0, 200, 282)
    _step_until(world, lambda: len(received) > 0)
    assert received and received[0].new_tier == 1


def test_different_tiers_do_not_merge():
    bus = EventBus()
    world = PhysicsWorld(bus)
    world.spawn(0, 200, 300)
    world.spawn(1, 200, 260)
    _step_until(world, lambda: False, max_steps=120)
    tiers = sorted(s.tier for s in world.snacks)
    assert tiers == [0, 1], "다른 단계끼리는 합쳐지지 않아야 한다"


def test_clear_removes_all():
    bus = EventBus()
    world = PhysicsWorld(bus)
    for _ in range(5):
        world.spawn(0, 200, 200)
    world.clear()
    assert len(world.snacks) == 0
