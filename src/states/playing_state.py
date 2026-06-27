"""플레이 상태: 입력(조준/드롭), 물리 진행, 게임오버 판정, 렌더."""
import random
import pygame

from src.config import WIDTH, WALL, DROP_Y, TIERS, DROPPABLE
from src.states.base_state import BaseState
from src.events.events import GameOver


class PlayingState(BaseState):
    DROP_COOLDOWN = 0.48
    DANGER_HOLD = 1.1

    def on_enter(self) -> None:
        self.aim_x = WIDTH / 2
        self.current = random.choice(DROPPABLE)
        self.next = random.choice(DROPPABLE)
        self.cooldown = 0.0
        self.danger_t = 0.0

    def _clamp_aim(self) -> None:
        r = TIERS[self.current].radius
        self.aim_x = max(WALL + r, min(WIDTH - WALL - r, self.aim_x))

    def handle_event(self, event) -> None:
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            self.aim_x = event.pos[0]
            self._clamp_aim()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.aim_x = event.pos[0]
            self._drop()

    def _drop(self) -> None:
        if self.cooldown > 0:
            return
        self._clamp_aim()
        self.game.world.spawn(self.current, self.aim_x, DROP_Y)
        self.current, self.next = self.next, random.choice(DROPPABLE)
        self.cooldown = self.DROP_COOLDOWN

    def update(self, dt: float) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)
        self.game.world.step(dt)
        self.game.particles.update(dt)
        if self.game.world.is_in_danger():
            self.danger_t += dt
            if self.danger_t >= self.DANGER_HOLD:
                from src.states.gameover_state import GameOverState
                self.game.bus.publish(GameOver(self.game.score.score))
                self.game.change_state(GameOverState(self.game))
        else:
            self.danger_t = 0.0

    def draw(self, surface) -> None:
        r = self.game.renderer
        r.draw_background(surface)
        r.draw_danger_line(surface)
        if self.cooldown <= 0:
            r.draw_preview(surface, self.aim_x, self.current)
        for snack in self.game.world.snacks:
            r.draw_snack(surface, snack.position.x, snack.position.y, snack.tier)
        r.draw_particles(surface, self.game.particles.particles)
        r.draw_next(surface, self.next)
        r.draw_text(surface, f"SCORE {self.game.score.score}", 19, (150, 100, 40), topleft=(WALL, 10))
        r.draw_text(surface, f"BEST {self.game.score.best}", 13, (160, 140, 200), topleft=(WALL, 33))
