"""오디오 시스템: 머지/생성/펑 이벤트에 merge.mp3 재생 (Observer).

assets/merge.mp3 가 있으면 재생하고, 없거나 믹서 초기화 실패 시 조용히 무시한다.
"""
import os

from src.events.event_bus import EventBus
from src.events.events import SnackMerged, BugiCreated, BugiPopped

try:
    import pygame
except Exception:  # pragma: no cover
    pygame = None


class AudioSystem:
    def __init__(self, bus: EventBus, assets_dir: str = "assets") -> None:
        self.enabled = False
        self._sound = None
        if pygame is not None:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                self.enabled = True
            except Exception:
                self.enabled = False

        self._load(os.path.join(assets_dir, "merge.mp3"))

        bus.subscribe(SnackMerged, lambda e: self.play())
        bus.subscribe(BugiCreated, lambda e: self.play())
        bus.subscribe(BugiPopped, lambda e: self.play())

    def _load(self, path: str) -> None:
        if self.enabled and os.path.exists(path):
            try:
                self._sound = pygame.mixer.Sound(path)
            except Exception:
                pass

    def play(self) -> None:
        if self._sound is not None:
            try:
                self._sound.play()
            except Exception:
                pass
