"""파티클 시스템: 머지/생성/펑 이벤트에 반응해 입자를 뿌린다 (Observer).

pygame에 의존하지 않는 순수 데이터. 렌더러가 그려준다.
"""
import math
import random

from src.events.event_bus import EventBus
from src.events.events import SnackMerged, BugiCreated, BugiPopped


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "color")

    def __init__(self, x, y, vx, vy, color):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = 1.0
        self.color = color


class ParticleSystem:
    def __init__(self, bus: EventBus) -> None:
        self.particles: list[Particle] = []
        bus.subscribe(SnackMerged, lambda e: self.burst(e.x, e.y, (255, 215, 106), 10))
        bus.subscribe(BugiCreated, lambda e: self.burst(e.x, e.y, (255, 158, 199), 30))
        bus.subscribe(BugiPopped, lambda e: self.burst(e.x, e.y, (255, 240, 166), 26))

    def burst(self, x, y, color, n) -> None:
        for _ in range(n):
            a = random.random() * math.tau
            s = 60 + random.random() * 150
            self.particles.append(
                Particle(x, y, math.cos(a) * s, math.sin(a) * s - 60, color)
            )

    def update(self, dt: float) -> None:
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += 500 * dt
            p.life -= dt * 1.6
        self.particles = [p for p in self.particles if p.life > 0]

    def clear(self) -> None:
        self.particles.clear()
