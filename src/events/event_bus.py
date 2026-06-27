"""간단한 동기 이벤트 버스 (Observer / Publish-Subscribe 패턴).

물리 세계가 점수·효과음·파티클을 직접 알 필요 없이 이벤트만 발행하고,
각 시스템이 관심 있는 이벤트 타입을 구독한다 -> 결합도 감소.
"""
from collections import defaultdict
from typing import Callable, Type


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[Type, list[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type, handler: Callable) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event) -> None:
        for handler in self._subscribers[type(event)]:
            handler(event)
