"""최고기록 저장 시스템 (Observer).

GameOver 이벤트를 구독해 점수를 누적 기록하고, 상위 N개를 제공한다.
기록은 **평문(txt)이 아닌** gzip 바이너리로 저장하고 HMAC 서명을 붙여,
사용자가 파일을 열어보거나 손으로 점수를 위조하기 어렵게 한다.

주의: 서명 키가 실행 파일 안에 들어가므로 '캐주얼한 변조'를 막는 수준이다
(작정하고 리버싱하는 사람까지 막지는 못한다).

의존성 없음(표준 라이브러리만 사용): json, gzip, hmac, hashlib, os, sys.
"""
import gzip
import hashlib
import hmac
import json
import os
import sys

from src.events.event_bus import EventBus
from src.events.events import GameOver

_SECRET = b"moongnyang-snackbox-record-v1"   # 서명용 키(변조 방지)
_SIG_LEN = 32                                 # sha256 digest 길이
_MAX_KEEP = 20                                # 내부 보관 개수
_FILE_NAME = "records.dat"


def _data_dir() -> str:
    """사용자별 쓰기 가능한 폴더. (윈도우: %LOCALAPPDATA%\\MoongNyangSnackBox)

    PyInstaller --onefile 에서는 실행 시 임시폴더(cwd)가 삭제되므로
    번들 안이 아니라 이 영구 폴더에 저장해야 기록이 유지된다.
    """
    base = (os.environ.get("LOCALAPPDATA")
            or os.environ.get("APPDATA")
            or os.path.expanduser("~"))
    path = os.path.join(base, "MoongNyangSnackBox")
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        path = os.path.expanduser("~")
    return path


class HighScoreStore:
    def __init__(self, bus: EventBus, path: str | None = None) -> None:
        self.path = path or os.path.join(_data_dir(), _FILE_NAME)
        self.records: list[int] = self._load()
        bus.subscribe(GameOver, self._on_gameover)

    # --- 이벤트 ---
    def _on_gameover(self, event: GameOver) -> None:
        if event.score > 0:
            self.add(int(event.score))

    def add(self, score: int) -> None:
        self.records = sorted(self.records + [score], reverse=True)[:_MAX_KEEP]
        self._save()

    def top(self, n: int = 3) -> list[int]:
        return self.records[:n]

    # --- 저장/로드 (gzip + HMAC 서명) ---
    def _save(self) -> None:
        payload = json.dumps(self.records).encode("utf-8")
        sig = hmac.new(_SECRET, payload, hashlib.sha256).digest()
        try:
            with open(self.path, "wb") as f:
                f.write(gzip.compress(sig + payload))
        except OSError:
            pass

    def _load(self) -> list[int]:
        try:
            with open(self.path, "rb") as f:
                blob = gzip.decompress(f.read())
            sig, payload = blob[:_SIG_LEN], blob[_SIG_LEN:]
            expected = hmac.new(_SECRET, payload, hashlib.sha256).digest()
            if not hmac.compare_digest(sig, expected):
                return []  # 변조/손상 → 기록 무시
            data = json.loads(payload.decode("utf-8"))
            return sorted((int(x) for x in data), reverse=True)[:_MAX_KEEP]
        except Exception:
            return []