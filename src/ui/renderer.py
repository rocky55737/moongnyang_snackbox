"""pygame 렌더러: 배경/간식(이미지)/순서표/팝업/파티클/텍스트 그리기 전담."""
import os
import pygame

from src.config import (
    WIDTH, HEIGHT, WALL, GROUND_TOP, DROP_Y, DANGER_Y, CHART_H,
    TIERS, BG_TOP, BG_BOTTOM, DANGER_COLOR, LAVENDER, CHART_BG,
)

_CHART_ICON = CHART_H - 6   # 하단 순서표 아이콘 크기
_POPUP_W = 220
_POPUP_H = 175
_POPUP_ICON = 80             # 팝업 내 음식 이미지 크기


class Renderer:
    def __init__(self) -> None:
        pygame.font.init()
        self._font_path = self._find_korean_font()
        self._font_cache: dict[int, pygame.font.Font] = {}
        self._bg = self._make_background()
        self._chart_bg = self._make_chart_bg()

        # 원본 이미지 로드
        self._raw_imgs: list[pygame.Surface | None] = self._load_raw()
        self._secrete_raw: pygame.Surface | None = self._load_one(
            os.path.join("assets", "secrete.png")
        )

        # 간식 크기별 미리 스케일 (radius*2 x radius*2)
        self._snack_imgs: list[pygame.Surface | None] = self._scale_snack()
        # 하단 순서표 아이콘 크기
        self._chart_imgs: list[pygame.Surface | None] = self._scale_all(_CHART_ICON)
        self._chart_secret: pygame.Surface | None = (
            pygame.transform.smoothscale(self._secrete_raw, (_CHART_ICON, _CHART_ICON))
            if self._secrete_raw else None
        )

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

    # --- 이미지 로딩/스케일 ---
    def _load_one(self, path: str) -> "pygame.Surface | None":
        if os.path.exists(path):
            try:
                return pygame.image.load(path).convert_alpha()
            except Exception:
                pass
        return None

    def _crop_to_content(self, img: pygame.Surface) -> pygame.Surface:
        """투명 패딩을 제거해 음식 콘텐츠 영역만 남긴다.

        샘플링으로 비투명 픽셀 범위를 찾아 크롭하므로
        원본 크기와 무관하게 물리 원에 딱 맞게 스케일된다.
        """
        w, h = img.get_size()
        step = max(3, min(w, h) // 40)
        min_x = min_y = 99999
        max_x = max_y = -1
        for x in range(0, w, step):
            for y in range(0, h, step):
                if img.get_at((x, y))[3] > 20:
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
                    if y < min_y: min_y = y
                    if y > max_y: max_y = y
        if max_x < 0:
            return img  # 알파 정보 없음 — 원본 반환
        pad = step * 2
        min_x = max(0, min_x - pad)
        min_y = max(0, min_y - pad)
        max_x = min(w - 1, max_x + pad)
        max_y = min(h - 1, max_y + pad)
        cw = max_x - min_x + 1
        ch = max_y - min_y + 1
        result = pygame.Surface((cw, ch), pygame.SRCALPHA)
        result.fill((0, 0, 0, 0))
        result.blit(img, (0, 0), pygame.Rect(min_x, min_y, cw, ch))
        return result

    def _load_raw(self) -> list:
        imgs = []
        for i in range(len(TIERS)):
            img = self._load_one(os.path.join("assets", f"tier_{i}.png"))
            if img is not None:
                img = self._crop_to_content(img)
            imgs.append(img)
        return imgs

    def _scale_snack(self) -> list:
        imgs = []
        for i, spec in enumerate(TIERS):
            size = max(1, int(spec.radius * 2))
            raw = self._raw_imgs[i]
            imgs.append(
                pygame.transform.smoothscale(raw, (size, size)) if raw else None
            )
        return imgs

    def _scale_all(self, size: int) -> list:
        return [
            pygame.transform.smoothscale(raw, (size, size)) if raw else None
            for raw in self._raw_imgs
        ]

    # --- 배경 ---
    def _make_background(self) -> pygame.Surface:
        surf = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / HEIGHT
            color = [int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)]
            pygame.draw.line(surf, color, (0, y), (WIDTH, y))
        return surf

    def _make_chart_bg(self) -> pygame.Surface:
        surf = pygame.Surface((WIDTH, CHART_H))
        surf.fill(CHART_BG)
        return surf

    def draw_background(self, surface) -> None:
        surface.blit(self._bg, (0, 0))
        surface.blit(self._chart_bg, (0, HEIGHT))

    def draw_danger_line(self, surface) -> None:
        x, dash, gap = WALL, 7, 8
        while x < WIDTH - WALL:
            pygame.draw.line(surface, DANGER_COLOR, (x, DANGER_Y),
                             (min(x + dash, WIDTH - WALL), DANGER_Y), 2)
            x += dash + gap

    # --- 간식 (이미지 기반) ---
    def draw_snack(self, surface, x, y, tier, scale=1.0) -> None:
        spec = TIERS[tier]
        cx, cy = int(x), int(y)
        img = self._snack_imgs[tier]
        if img:
            if abs(scale - 1.0) > 0.001:
                size = max(1, int(spec.radius * 2 * scale))
                img = pygame.transform.smoothscale(img, (size, size))
            surface.blit(img, img.get_rect(center=(cx, cy)))
        else:
            r = int(spec.radius * scale)
            pygame.draw.circle(surface, (180, 180, 180), (cx, cy), r)
            pygame.draw.circle(surface, (140, 140, 140), (cx, cy), r, max(2, int(r * 0.07)))

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

    # --- 하단 순서표 ---
    def draw_tier_chart(self, surface, discovered: set) -> None:
        n = len(TIERS)
        slot_w = (WIDTH - 2 * WALL) // n
        pad_y = (CHART_H - _CHART_ICON) // 2
        chart_y = HEIGHT + pad_y
        # 중앙 정렬
        total_w = slot_w * n
        start_x = WALL + ((WIDTH - 2 * WALL) - total_w) // 2

        for i in range(n):
            slot_x = start_x + i * slot_w + (slot_w - _CHART_ICON) // 2
            if i in discovered:
                img = self._chart_imgs[i]
                if img:
                    surface.blit(img, (slot_x, chart_y))
                else:
                    pygame.draw.rect(surface, (130, 130, 130),
                                     (slot_x, chart_y, _CHART_ICON, _CHART_ICON),
                                     border_radius=3)
            else:
                if self._chart_secret:
                    surface.blit(self._chart_secret, (slot_x, chart_y))
                else:
                    pygame.draw.rect(surface, (55, 45, 80),
                                     (slot_x, chart_y, _CHART_ICON, _CHART_ICON),
                                     border_radius=3)

    # --- 발견 팝업 ---
    def draw_popup(self, surface, tier: int) -> pygame.Rect:
        """발견 팝업을 그리고 X 버튼 rect을 반환한다."""
        px = (WIDTH - _POPUP_W) // 2
        py = (HEIGHT - _POPUP_H) // 2

        # 반투명 오버레이
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 10, 50, 180))
        surface.blit(overlay, (0, 0))

        # 팝업 박스
        pygame.draw.rect(surface, (255, 245, 255),
                         (px, py, _POPUP_W, _POPUP_H), border_radius=14)
        pygame.draw.rect(surface, LAVENDER,
                         (px, py, _POPUP_W, _POPUP_H), 3, border_radius=14)

        # NEW! 텍스트
        self.draw_text(surface, "NEW!", 20, (138, 107, 255),
                       center=(WIDTH // 2, py + 24))

        # 음식 이미지
        raw = self._raw_imgs[tier]
        icon_y = py + _POPUP_H // 2
        if raw:
            icon = pygame.transform.smoothscale(raw, (_POPUP_ICON, _POPUP_ICON))
            surface.blit(icon, icon.get_rect(center=(WIDTH // 2, icon_y)))
        else:
            pygame.draw.circle(surface, (180, 180, 180),
                               (WIDTH // 2, icon_y), _POPUP_ICON // 2)

        # 음식 이름
        self.draw_text(surface, TIERS[tier].name, 16, (60, 30, 80),
                       center=(WIDTH // 2, py + _POPUP_H - 22))

        # X 버튼 (오른쪽 상단)
        x_rect = pygame.Rect(px + _POPUP_W - 30, py + 8, 22, 22)
        pygame.draw.circle(surface, (210, 185, 230), x_rect.center, 11)
        cx2, cy2 = x_rect.center
        pygame.draw.line(surface, (80, 50, 110), (cx2 - 4, cy2 - 4), (cx2 + 4, cy2 + 4), 2)
        pygame.draw.line(surface, (80, 50, 110), (cx2 + 4, cy2 - 4), (cx2 - 4, cy2 + 4), 2)

        return x_rect

    # --- 텍스트 ---
    def draw_text(self, surface, text, size, color,
                  center=None, topleft=None, topright=None):
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
