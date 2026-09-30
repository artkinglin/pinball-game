"""Main game state and update loop."""

from __future__ import annotations

import pygame
import pymunk

import settings as S
from entities import Ball, Flipper, Plunger
from render import draw_ball, draw_flipper, draw_plunger, draw_table, draw_text, pixel_font
from table import Table


class Game:
    """Owns pinball state, simulation, and rendering."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.space = pymunk.Space()
        self.space.gravity = (0, S.GRAVITY)
        self.table = Table(self.space)
        self.ball = Ball(self.space, S.PLUNGER_SPAWN)
        self.left_flipper = Flipper(
            self.space, S.LEFT_FLIPPER_PIVOT, S.LEFT_FLIPPER_REST, S.LEFT_FLIPPER_ACTIVE, True
        )
        self.right_flipper = Flipper(
            self.space, S.RIGHT_FLIPPER_PIVOT, S.RIGHT_FLIPPER_REST, S.RIGHT_FLIPPER_ACTIVE, False
        )
        self.plunger = Plunger()
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
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LSHIFT, pygame.K_LEFT):
                self.left_flipper.pressed = True
            if event.key in (pygame.K_RSHIFT, pygame.K_RIGHT):
                self.right_flipper.pressed = True
            if event.key == pygame.K_SPACE:
                self.plunger.held = True
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LSHIFT, pygame.K_LEFT):
                self.left_flipper.pressed = False
            if event.key in (pygame.K_RSHIFT, pygame.K_RIGHT):
                self.right_flipper.pressed = False
            if event.key == pygame.K_SPACE and self.plunger.held:
                impulse = self.plunger.release_impulse()
                if self.ball.body.position.x > S.PLUNGER_LANE_X - 24 and self.ball.body.position.y > 690:
                    self.ball.body.apply_impulse_at_local_point((0, -impulse))
        return True

    def update(self, dt: float) -> None:
        if self.paused:
            return
        self.left_flipper.update(dt)
        self.right_flipper.update(dt)
        self.plunger.update(dt)
        step = S.FIXED_DT / S.PHYSICS_SUBSTEPS
        for _ in range(S.PHYSICS_SUBSTEPS):
            self.space.step(step)
            self.ball.cap_speed()

    def draw(self) -> None:
        self.screen.fill(S.BLACK)
        draw_table(self.screen, self.table)
        draw_flipper(self.screen, self.left_flipper)
        draw_flipper(self.screen, self.right_flipper)
        draw_plunger(self.screen, self.plunger.power)
        draw_ball(self.screen, tuple(self.ball.body.position), self.crt)
        draw_text(self.screen, self.title_font, "NEON PINBALL", (S.WIDTH // 2, 24), S.MAGENTA, center=True)
        draw_text(self.screen, self.hud_font, "TABLE ONLINE", (S.HUD_MARGIN, 48), S.GREEN)
        if self.paused:
            draw_text(self.screen, self.title_font, "PAUSED", (S.WIDTH // 2, S.HEIGHT // 2), S.YELLOW, center=True)
