"""도메인 이벤트 정의(Observer 패턴에서 발행/구독되는 메시지)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SnackMerged:
    new_tier: int
    x: float
    y: float


@dataclass(frozen=True)
class BugiCreated:
    x: float
    y: float


@dataclass(frozen=True)
class BugiPopped:
    x: float
    y: float


@dataclass(frozen=True)
class GameOver:
    score: int
