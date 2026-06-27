"""게임오버 상태: 결과 오버레이 표시, 입력 시 재시작."""
import pygame

from src.config import WIDTH, HEIGHT, MAX_TIER
from src.states.base_state import BaseState


class GameOverState(BaseState):
    def on_enter(self) -> None:
        self.made_bugi = any(s.tier == MAX_TIER for s in self.game.world.snacks)

    def handle_event(self, event) -> None:
        if event.type in (pygame.MOUSEBUTTONUP, pygame.KEYDOWN):
            self.game.restart()

    def update(self, dt: float) -> None:
        self.game.particles.update(dt)

    def draw(self, surface) -> None:
        r = self.game.renderer
        r.draw_background(surface)
        r.draw_danger_line(surface)
        for snack in self.game.world.snacks:
            r.draw_snack(surface, snack.position.x, snack.position.y, snack.tier)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((36, 26, 71, 210))
        surface.blit(overlay, (0, 0))

        title = "부기 완성! 대성공 🎉" if self.made_bugi else "간식 상자가 꽉 찼어요!"
        r.draw_text(surface, title, 25, (255, 158, 199), center=(WIDTH // 2, HEIGHT // 2 - 42))
        r.draw_text(surface, f"점수 {self.game.score.score}", 30, (255, 215, 106), center=(WIDTH // 2, HEIGHT // 2 + 4))
        r.draw_text(surface, "클릭 또는 아무 키로 다시하기", 16, (220, 210, 255), center=(WIDTH // 2, HEIGHT // 2 + 48))
