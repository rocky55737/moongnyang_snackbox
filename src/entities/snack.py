"""간식 엔티티: 물리 바디/형상과 단계(tier)를 묶는다."""
from src.config import TIERS, TierSpec


class Snack:
    __slots__ = ("tier", "body", "shape", "born", "merging")

    def __init__(self, tier: int, body, shape, born: float) -> None:
        self.tier = tier
        self.body = body
        self.shape = shape
        self.born = born
        self.merging = False

    @property
    def spec(self) -> TierSpec:
        return TIERS[self.tier]

    @property
    def position(self):
        return self.body.position
