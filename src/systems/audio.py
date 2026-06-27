"""오디오 시스템: 이벤트에 맞춰 효과음 재생 (Observer).

assets/ 에 wav가 있으면 재생하고, 없거나 믹서 초기화 실패 시 조용히 무시한다.
(외부 의존성 없이 동작하도록 설계)
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
        self.sounds: dict[str, object] = {}
        if pygame is not None:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                self.enabled = True
            except Exception:
                self.enabled = False

        self._load("merge", os.path.join(assets_dir, "merge.wav"))
        self._load("bugi", os.path.join(assets_dir, "bugi.wav"))

        bus.subscribe(SnackMerged, lambda e: self.play("merge"))
        bus.subscribe(BugiCreated, lambda e: self.play("bugi"))
        bus.subscribe(BugiPopped, lambda e: self.play("bugi"))

    def _load(self, key: str, path: str) -> None:
        if self.enabled and os.path.exists(path):
            try:
                self.sounds[key] = pygame.mixer.Sound(path)
            except Exception:
                pass

    def play(self, key: str) -> None:
        snd = self.sounds.get(key)
        if snd is not None:
            try:
                snd.play()
            except Exception:
                pass
