"""오디오 시스템: 이벤트에 맞춰 효과음 재생 (Observer).

assets/merge.mp3 — 머지/생성/펑
assets/find.mp3  — 새 간식 최초 발견
"""
import os

from src.events.event_bus import EventBus
from src.events.events import SnackMerged, BugiCreated, BugiPopped, TierDiscovered

try:
    import pygame
except Exception:  # pragma: no cover
    pygame = None


class AudioSystem:
    def __init__(self, bus: EventBus, assets_dir: str = "assets") -> None:
        self.enabled = False
        self._sounds: dict[str, object] = {}
        if pygame is not None:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                self.enabled = True
            except Exception:
                self.enabled = False

        self._load("merge", os.path.join(assets_dir, "merge.mp3"))
        self._load("find",  os.path.join(assets_dir, "find.mp3"))

        bus.subscribe(SnackMerged,     lambda _: self.play("merge"))
        bus.subscribe(BugiCreated,     lambda _: self.play("merge"))
        bus.subscribe(BugiPopped,      lambda _: self.play("merge"))
        bus.subscribe(TierDiscovered,  lambda _: self.play("find"))

    def _load(self, key: str, path: str) -> None:
        if self.enabled and os.path.exists(path):
            try:
                self._sounds[key] = pygame.mixer.Sound(path)
            except Exception:
                pass

    def play(self, key: str) -> None:
        snd = self._sounds.get(key)
        if snd is not None:
            try:
                snd.play()
            except Exception:
                pass
