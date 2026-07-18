"""Game: 메인 루프 + 상태 전환 + 시스템 조립 (컴포지션 루트)."""
import pygame

from src.config import WIDTH, WINDOW_HEIGHT, LEFT_W, FPS
from src.events.event_bus import EventBus
from src.physics.world import PhysicsWorld
from src.systems.score import ScoreSystem
from src.systems.particles import ParticleSystem
from src.systems.audio import AudioSystem
from src.systems.discovery import DiscoverySystem
from src.systems.highscore import HighScoreStore
from src.systems.video_player import CharacterVideo
from src.ui.renderer import Renderer
from src.states.playing_state import PlayingState


class Game:
    def __init__(self) -> None:
        pygame.init()

        # 컴포지션 루트: 이벤트 버스를 공유하며 시스템들을 연결한다.
        self.bus = EventBus()

        # 캐릭터 비디오 스트립 (게임 오른쪽). 머지→Yay, 게임오버→Crying 을 구독한다.
        self.video = CharacterVideo(self.bus, target_height=WINDOW_HEIGHT)
        # 창 = [왼쪽 최고기록 패널] + [게임] + [영상 스트립]
        window_w = LEFT_W + WIDTH + self.video.strip_w

        self.screen = pygame.display.set_mode((window_w, WINDOW_HEIGHT))
        pygame.display.set_caption("뭉냥이의 간식 상자")
        self.clock = pygame.time.Clock()

        # 게임 화면은 별도 서피스에 그린 뒤 왼쪽 패널만큼 오른쪽으로 blit
        self.play_surf = pygame.Surface((WIDTH, WINDOW_HEIGHT))

        self.world = PhysicsWorld(self.bus)
        self.score = ScoreSystem(self.bus)
        self.particles = ParticleSystem(self.bus)
        self.audio = AudioSystem(self.bus)
        self.discovery = DiscoverySystem(self.bus)
        self.highscore = HighScoreStore(self.bus)
        self.renderer = Renderer()

        self.running = True
        self.state = None
        self.change_state(PlayingState(self))

    def change_state(self, state) -> None:
        self.state = state
        state.on_enter()

    def restart(self) -> None:
        self.world.clear()
        self.score.reset()
        self.particles.clear()
        self.discovery.reset()
        self.video.reset()
        self.change_state(PlayingState(self))

    def run(self, max_frames=None) -> None:
        frames = 0
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 1 / 30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.state.handle_event(event)
            self.video.update(dt)
            self.state.update(dt)
            self.state.draw(self.play_surf)
            self.renderer.draw_leaderboard(self.screen, self.highscore.top(3))
            self.screen.blit(self.play_surf, (LEFT_W, 0))
            self.video.draw(self.screen, LEFT_W + WIDTH, 0)
            pygame.display.flip()
            frames += 1
            if max_frames is not None and frames >= max_frames:
                break
        pygame.quit()