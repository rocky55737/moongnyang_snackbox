"""캐릭터 비디오: 게임 상태에 따라 클립을 바꿔 재생한다 (Observer).

- 평소:        Standing 무한 루프
- 간식 합쳐짐:  Yay 1회 재생 후 Standing 복귀
- 박스 가득 참: Crying 재생(루프)

각 mp4의 가로 중앙 1/3을 크롭해 target_height에 맞춰 스케일하고,
게임 오른쪽 스트립으로 표시한다. cv2 없거나 파일이 없으면 조용히 비활성화.

파일명은 'MoonNyang_*' / 'MoongNyang_*' 두 철자를 모두 탐색한다.
"""
import os

try:
    import cv2
    _CV2_OK = True
except ImportError:
    _CV2_OK = False

try:
    import pygame
    import pygame.surfarray
except ImportError:
    pygame = None  # type: ignore

from src.config import WINDOW_HEIGHT
from src.events.event_bus import EventBus
from src.events.events import SnackMerged, GameOver

# 상태별 후보 파일명(철자 혼용 대비: Moon / Moong)
_ROLE_FILES = {
    "standing": ["MoongNyang_Standing.mp4", "MoonNyang_Standing.mp4"],
    "yay":      ["MoonNyang_Yay.mp4", "MoongNyang_Yay.mp4"],
    "crying":   ["MoongNyang_Crying.mp4", "MoonNyang_Crying.mp4"],
}
# 루프로 재생하는 상태(그 외는 1회 재생 후 다음 상태로 전환)
_LOOPING = {"standing", "crying"}


class _Clip:
    """단일 mp4 클립 디코더(크롭·스케일 포함)."""

    def __init__(self, path: str, target_w: int, target_h: int) -> None:
        self.ok = False
        self.fps = 30.0
        self._cap = cv2.VideoCapture(path)
        if not self._cap.isOpened():
            return
        w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if w <= 0 or h <= 0:
            self._cap.release()
            return
        self.fps = self._cap.get(cv2.CAP_PROP_FPS) or 30.0
        self._cx = w // 3
        self._cw = w // 3
        self._tw = target_w
        self._th = target_h
        self.ok = True

    def rewind(self) -> None:
        if self.ok:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def read(self, loop: bool):
        """다음 프레임 Surface를 반환. (surface|None, ended:bool)"""
        if not self.ok:
            return None, True
        ret, frame = self._cap.read()
        if not ret:
            if not loop:
                return None, True
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
            if not ret:
                return None, True
        cropped = frame[:, self._cx:self._cx + self._cw]
        scaled = cv2.resize(cropped, (self._tw, self._th), interpolation=cv2.INTER_LINEAR)
        rgb = cv2.cvtColor(scaled, cv2.COLOR_BGR2RGB)
        return pygame.surfarray.make_surface(rgb.swapaxes(0, 1)), False

    def release(self) -> None:
        if getattr(self, "_cap", None) is not None:
            self._cap.release()


class CharacterVideo:
    def __init__(self, bus: EventBus, assets_dir: str = "assets",
                 target_height: int = WINDOW_HEIGHT) -> None:
        self.strip_w = 0
        self.strip_h = target_height
        self._clips: dict[str, _Clip] = {}
        self._state = "standing"
        self._next = "standing"      # 1회 재생이 끝나면 돌아갈 상태
        self._surface = None
        self._acc = 0.0

        if not _CV2_OK or pygame is None:
            return

        paths = {role: self._resolve(assets_dir, names)
                 for role, names in _ROLE_FILES.items()}

        # 스트립 크기 결정: standing → yay → crying 순으로 먼저 열리는 것 기준
        for role in ("standing", "yay", "crying"):
            p = paths.get(role)
            if not p:
                continue
            probe = cv2.VideoCapture(p)
            if probe.isOpened():
                w = int(probe.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(probe.get(cv2.CAP_PROP_FRAME_HEIGHT))
                probe.release()
                if w > 0 and h > 0:
                    self.strip_w = max(1, int((w // 3) * (target_height / h)))
                    break
            probe.release()

        if self.strip_w == 0:
            return

        for role, p in paths.items():
            if p:
                clip = _Clip(p, self.strip_w, self.strip_h)
                if clip.ok:
                    self._clips[role] = clip

        # 구독: 머지 → Yay, 게임오버 → Crying
        bus.subscribe(SnackMerged, self._on_merged)
        bus.subscribe(GameOver, self._on_gameover)

        self._prime()

    # --- 경로 탐색 ---
    @staticmethod
    def _resolve(assets_dir: str, names):
        for n in names:
            p = os.path.join(assets_dir, n)
            if os.path.exists(p):
                return p
        return None

    # --- 상태 전환 ---
    def _switch(self, state: str, nxt: str) -> None:
        target = state if state in self._clips else "standing"
        self._state = target
        self._next = nxt
        clip = self._clips.get(target)
        if clip:
            clip.rewind()
        self._acc = 0.0
        self._prime()

    def _on_merged(self, _event) -> None:
        if "yay" in self._clips:
            self._switch("yay", "standing")

    def _on_gameover(self, _event) -> None:
        self._switch("crying", "crying")

    def reset(self) -> None:
        """재시작 시 Standing 루프로 복귀."""
        self._switch("standing", "standing")

    # --- 렌더 프레임 갱신 ---
    def _current_clip(self):
        return self._clips.get(self._state) or self._clips.get("standing")

    def _prime(self) -> None:
        clip = self._current_clip()
        if clip:
            surf, _ = clip.read(loop=True)
            if surf is not None:
                self._surface = surf

    def update(self, dt: float) -> None:
        clip = self._current_clip()
        if clip is None:
            return
        self._acc += dt
        frame_dt = 1.0 / clip.fps
        while self._acc >= frame_dt:
            self._acc -= frame_dt
            loop = self._state in _LOOPING
            surf, ended = clip.read(loop=loop)
            if ended and not loop:
                # 1회 재생 종료 → 다음 상태로
                self._state = self._next if self._next in self._clips else "standing"
                nxt = self._current_clip()
                if nxt:
                    nxt.rewind()
                self._prime()
                break
            if surf is not None:
                self._surface = surf

    def draw(self, surface, x: int, y: int) -> None:
        if self._surface is not None:
            surface.blit(self._surface, (x, y))

    def __del__(self) -> None:
        for clip in getattr(self, "_clips", {}).values():
            clip.release()