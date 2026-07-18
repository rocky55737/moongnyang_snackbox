"""플레이 상태: 입력(조준/드롭), 물리 진행, 게임오버 판정, 렌더."""
import random
import pygame

from src.config import WIDTH, WALL, DROP_Y, TIERS, DROPPABLE, LEFT_W
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
        self._popup: int | None = None     # 현재 표시 중인 팝업의 tier
        self._popup_x_rect = None          # X 버튼 클릭 영역

    def _clamp_aim(self) -> None:
        r = TIERS[self.current].radius
        self.aim_x = max(WALL + r, min(WIDTH - WALL - r, self.aim_x))

    def handle_event(self, event) -> None:
        # 마우스 이벤트만 처리(그 외 이벤트엔 .pos 가 없음)
        if event.type not in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            return
        # 화면은 왼쪽 패널(LEFT_W)만큼 밀려 있으므로 마우스 x를 보정한다.
        mx = event.pos[0] - LEFT_W

        if self._popup is not None:
            # 팝업이 열려 있으면 X 클릭만 처리
            if event.type == pygame.MOUSEBUTTONUP:
                if self._popup_x_rect and self._popup_x_rect.collidepoint((mx, event.pos[1])):
                    self._popup = None
            return

        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            self.aim_x = mx
            self._clamp_aim()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.aim_x = mx
            self._drop()

    def _drop(self) -> None:
        if self.cooldown > 0:
            return
        self._clamp_aim()
        self.game.world.spawn(self.current, self.aim_x, DROP_Y)
        self.game.discovery.check_new(self.current)
        self.current, self.next = self.next, random.choice(DROPPABLE)
        self.cooldown = self.DROP_COOLDOWN

    def update(self, dt: float) -> None:
        # 팝업이 없을 때만 다음 팝업을 꺼낸다
        if self._popup is None:
            pending = self.game.discovery.pop_pending()
            if pending is not None:
                self._popup = pending

        self.game.particles.update(dt)

        # 팝업 표시 중에는 물리 정지
        if self._popup is not None:
            return

        self.cooldown = max(0.0, self.cooldown - dt)
        self.game.world.step(dt)
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
        if self.cooldown <= 0 and self._popup is None:
            r.draw_preview(surface, self.aim_x, self.current)
        for snack in self.game.world.snacks:
            r.draw_snack(surface, snack.position.x, snack.position.y, snack.tier)
        r.draw_particles(surface, self.game.particles.particles)
        r.draw_next(surface, self.next)
        r.draw_text(surface, f"SCORE {self.game.score.score}", 19, (150, 100, 40), topleft=(WALL, 10))
        r.draw_text(surface, f"BEST {self.game.score.best}", 13, (160, 140, 200), topleft=(WALL, 33))
        r.draw_tier_chart(surface, self.game.discovery.discovered)

        if self._popup is not None:
            self._popup_x_rect = r.draw_popup(surface, self._popup)