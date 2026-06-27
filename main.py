"""엔트리 포인트.

실행:        python main.py
헤드리스 점검: python main.py --smoke
"""
import os
import sys


def main() -> None:
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
