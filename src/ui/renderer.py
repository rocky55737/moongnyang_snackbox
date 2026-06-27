"""pygame 렌더러: 배경/간식/미리보기/파티클/텍스트 그리기를 전담.

게임 로직과 분리돼 있어, 비주얼만 따로 교체(스프라이트 이미지 등)하기 쉽다.
"""
import os
import pygame

from src.config import (
    WIDTH, HEIGHT, WALL, GROUND_TOP, DROP_Y, DANGER_Y,
    TIERS, BG_TOP, BG_BOTTOM, DANGER_COLOR, LAVENDER,
)


class Renderer:
    def __init__(self) -> None:
        pygame.font.init()
        self._font_path = self._find_korean_font()
        self._font_cache: dict[int, pygame.font.Font] = {}
        self._bg = self._make_background()

    # --- 폰트 ---
    def _find_korean_font(self):
        local = os.path.join("assets", "font.ttf")
        if os.path.exists(local):
            return local
        return pygame.font.match_font(
            "nanumgothic,malgungothic,applesdgothicneo,notosanscjkkr,notosanskr,arialunicode"
        )

    def font(self, size: int) -> pygame.font.Font:
        size = max(8, int(size))
        if size not in self._font_cache:
            self._font_cache[size] = (
                pygame.font.Font(self._font_path, size)
                if self._font_path else pygame.font.SysFont(None, size)
            )
        return self._font_cache[size]

    # --- 배경 ---
    def _make_background(self) -> pygame.Surface:
        surf = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = [int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)]
            pygame.draw.line(surf, color, (0, y), (WIDTH, y))
        return surf

    def draw_background(self, surface) -> None:
        surface.blit(self._bg, (0, 0))

    def draw_danger_line(self, surface) -> None:
        x, dash, gap = WALL, 7, 8
        while x < WIDTH - WALL:
            pygame.draw.line(surface, DANGER_COLOR, (x, DANGER_Y),
                             (min(x + dash, WIDTH - WALL), DANGER_Y), 2)
            x += dash + gap

    # --- 간식 ---
    def draw_snack(self, surface, x, y, tier, scale=1.0) -> None:
        spec = TIERS[tier]
        r = spec.radius * scale
        cx, cy = int(x), int(y)
        pygame.draw.circle(surface, spec.color, (cx, cy), int(r))
        pygame.draw.circle(surface, spec.ring, (cx, cy), int(r), max(2, int(r * 0.07)))
        # 광택
        gr = int(r * 0.32)
        if gr > 0:
            gloss = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
            pygame.draw.circle(gloss, (255, 255, 255, 90), (gr, gr), gr)
            surface.blit(gloss, (cx - int(r * 0.34) - gr, cy - int(r * 0.36) - gr))
        # 이름
        label = self.font(max(9, int(r * 0.42))).render(spec.name, True, (60, 40, 70))
        surface.blit(label, label.get_rect(center=(cx, cy)))

    def draw_preview(self, surface, x, tier) -> None:
        spec = TIERS[tier]
        pygame.draw.line(surface, LAVENDER, (int(x), int(DROP_Y + spec.radius)),
                         (int(x), GROUND_TOP), 1)
        self.draw_snack(surface, x, DROP_Y, tier)

    def draw_particles(self, surface, particles) -> None:
        for p in particles:
            a = max(0, min(255, int(p.life * 255)))
            s = pygame.Surface((7, 7), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p.color, a), (3, 3), 3)
            surface.blit(s, (int(p.x) - 3, int(p.y) - 3))

    def draw_next(self, surface, tier) -> None:
        self.draw_text(surface, "NEXT", 13, LAVENDER, topright=(WIDTH - WALL, 12))
        self.draw_snack(surface, WIDTH - WALL - 14, 34, tier, scale=0.30)

    # --- 텍스트 ---
    def draw_text(self, surface, text, size, color, center=None, topleft=None, topright=None):
        img = self.font(size).render(text, True, color)
        rect = img.get_rect()
        if center:
            rect.center = center
        if topleft:
            rect.topleft = topleft
        if topright:
            rect.topright = topright
        surface.blit(img, rect)
        return rect
