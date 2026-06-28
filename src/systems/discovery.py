"""발견 시스템: 처음 등장하는 간식 단계를 추적하고 팝업 큐를 관리한다."""
from src.events.event_bus import EventBus
from src.events.events import SnackMerged, TierDiscovered


class DiscoverySystem:
    def __init__(self, bus: EventBus) -> None:
        self._bus = bus
        self.discovered: set[int] = set()
        self._pending: list[int] = []
        bus.subscribe(SnackMerged, self._on_merged)

    def check_new(self, tier: int) -> None:
        """드롭 또는 외부에서 직접 호출 — tier가 처음이면 팝업 큐에 추가한다."""
        if tier not in self.discovered:
            self.discovered.add(tier)
            self._pending.append(tier)
            self._bus.publish(TierDiscovered(tier))

    def _on_merged(self, event: SnackMerged) -> None:
        self.check_new(event.new_tier)

    def pop_pending(self) -> int | None:
        return self._pending.pop(0) if self._pending else None

    def reset(self) -> None:
        self.discovered.clear()
        self._pending.clear()
