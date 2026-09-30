"""Main game state and update loop."""

from __future__ import annotations

import pygame
import pymunk

import settings as S
from render import draw_table, draw_text, pixel_font
from table import Table


class Game:
    """Owns pinball state, simulation, and rendering."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.space = pymunk.Space()
        self.space.gravity = (0, S.GRAVITY)
        self.table = Table(self.space)
        self.title_font = pixel_font(26)
        self.hud_font = pixel_font(18)
        self.paused = False
        self.crt = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            self.paused = not self.paused
        if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
            self.crt = not self.crt
        return True

    def update(self, dt: float) -> None:
        if self.paused:
            return
        step = S.FIXED_DT / S.PHYSICS_SUBSTEPS
        for _ in range(S.PHYSICS_SUBSTEPS):
            self.space.step(step)

    def draw(self) -> None:
        self.screen.fill(S.BLACK)
        draw_table(self.screen, self.table)
        draw_text(self.screen, self.title_font, "NEON PINBALL", (S.WIDTH // 2, 24), S.MAGENTA, center=True)
        draw_text(self.screen, self.hud_font, "TABLE ONLINE", (S.HUD_MARGIN, 48), S.GREEN)
        if self.paused:
            draw_text(self.screen, self.title_font, "PAUSED", (S.WIDTH // 2, S.HEIGHT // 2), S.YELLOW, center=True)
