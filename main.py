"""엔트리 포인트.

실행:        python main.py
헤드리스 점검: python main.py --smoke
"""
import os
import sys


def _fix_resource_path() -> None:
    # PyInstaller --onefile 번들에서는 assets 등 리소스가
    # sys._MEIPASS 임시 폴더에 압축 해제되므로 cwd를 맞춰준다.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        os.chdir(sys._MEIPASS)


def main() -> None:
    _fix_resource_path()
    smoke = "--smoke" in sys.argv
    if smoke:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    from src.game import Game

    game = Game()
    game.run(max_frames=180 if smoke else None)
    if smoke:
        print("smoke OK")


if __name__ == "__main__":
    main()
