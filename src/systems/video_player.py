"""비디오 플레이어: mp4 프레임을 읽어 pygame Surface로 반환.

중앙 1/3(가로) 크롭 후 target_height에 맞게 스케일해
게임 옆 스트립으로 표시한다. 영상이 끝나면 자동 루프.
파일이 없거나 cv2 import 실패 시 조용히 비활성화.
"""
import os

try:
    import cv2
    import numpy as np
    _CV2_OK = True
except ImportError:
    _CV2_OK = False

try:
    import pygame
    import pygame.surfarray
except ImportError:
    pygame = None  # type: ignore


class VideoPlayer:
    def __init__(self, path: str, target_height: int) -> None:
        self.strip_w = 0
        self._cap = None
        self._surface = None
        self._frame_acc = 0.0
        self._fps = 30.0

        if not _CV2_OK or not os.path.exists(path):
            return

        self._cap = cv2.VideoCapture(path)
        vid_w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        vid_h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._fps = self._cap.get(cv2.CAP_PROP_FPS) or 30.0

        # 가로 중앙 1/3 크롭 범위
        self._cx = vid_w // 3
        self._cw = vid_w // 3
        self._ch = vid_h

        # target_height 기준 스케일
        scale = target_height / vid_h
        self.strip_w = max(1, int(self._cw * scale))
        self.strip_h = target_height

        self._read_frame()  # 첫 프레임 로드

    # --- 내부 ---
    def _read_frame(self) -> None:
        if self._cap is None:
            return
        ret, frame = self._cap.read()
        if not ret:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self._cap.read()
            if not ret:
                return

        # 중앙 1/3 크롭
        cropped = frame[:, self._cx:self._cx + self._cw]
        # 스케일
        scaled = cv2.resize(cropped, (self.strip_w, self.strip_h),
                            interpolation=cv2.INTER_LINEAR)
        # BGR → RGB, (H,W,3) → (W,H,3) for pygame
        rgb = cv2.cvtColor(scaled, cv2.COLOR_BGR2RGB)
        self._surface = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))

    # --- 공개 ---
    def update(self, dt: float) -> None:
        if self._cap is None:
            return
        self._frame_acc += dt
        frame_dt = 1.0 / self._fps
        while self._frame_acc >= frame_dt:
            self._frame_acc -= frame_dt
            self._read_frame()

    def draw(self, surface, x: int, y: int) -> None:
        if self._surface is not None:
            surface.blit(self._surface, (x, y))

    def __del__(self) -> None:
        if self._cap is not None:
            self._cap.release()
