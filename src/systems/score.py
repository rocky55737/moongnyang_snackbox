"""점수 시스템: 머지/펑 이벤트를 구독해 점수를 갱신 (Observer)."""
from src.config import TIERS, BUGI_POP_BONUS
from src.events.event_bus import EventBus
from src.events.events import SnackMerged, BugiPopped


class ScoreSystem:
    def __init__(self, bus: EventBus) -> None:
        self.score = 0
        self.best = 0
        bus.subscribe(SnackMerged, self._on_merged)
        bus.subscribe(BugiPopped, self._on_popped)

    def _on_merged(self, event: SnackMerged) -> None:
        self.add(TIERS[event.new_tier].points)

    def _on_popped(self, event: BugiPopped) -> None:
        self.add(BUGI_POP_BONUS)

    def add(self, points: int) -> None:
        self.score += points
        self.best = max(self.best, self.score)

    def reset(self) -> None:
        self.score = 0
