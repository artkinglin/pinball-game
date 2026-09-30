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
        self.hit_events: list[str] = []
        self._setup_collisions()
        self.title_font = pixel_font(26)
        self.hud_font = pixel_font(18)
        self.paused = False
        self.crt = True

    def _setup_collisions(self) -> None:
        self.space.on_collision(1, 3, begin=self._hit_bumper)
        self.space.on_collision(1, 4, begin=self._hit_sling)
        self.space.on_collision(1, 5, begin=self._hit_target)
        self.space.on_collision(1, 6, begin=self._hit_lane)

    @staticmethod
    def _other_shape(arbiter: pymunk.Arbiter) -> pymunk.Shape:
        return arbiter.shapes[1]

    def _hit_bumper(self, arbiter: pymunk.Arbiter, _space: pymunk.Space, _data: dict) -> bool:
        shape = self._other_shape(arbiter)
        bumper = next(item for item in self.table.bumpers if item.shape is shape)
        if bumper.flash <= 0:
            direction = self.ball.body.position - pymunk.Vec2d(*bumper.position)
            if direction.length < 0.01:
                direction = pymunk.Vec2d(0, 1)
            self.ball.body.apply_impulse_at_world_point(direction.normalized() * S.BUMPER_IMPULSE, self.ball.body.position)
            bumper.flash = S.FLASH_TIME
            self.hit_events.append("bumper")
        return True

    def _hit_sling(self, arbiter: pymunk.Arbiter, _space: pymunk.Space, _data: dict) -> bool:
        shape = self._other_shape(arbiter)
        sling = next(item for item in self.table.slings if item.shape is shape)
        if sling.flash <= 0:
            self.ball.body.apply_impulse_at_local_point(sling.kick)
            sling.flash = S.FLASH_TIME
            self.hit_events.append("sling")
        return True

    def _hit_target(self, arbiter: pymunk.Arbiter, _space: pymunk.Space, _data: dict) -> bool:
        shape = self._other_shape(arbiter)
        target = next(item for item in self.table.targets if item.shape is shape)
        if not target.down:
            target.down = True
            target.flash = S.FLASH_TIME
            target.shape.sensor = True
            self.hit_events.append("target")
        return True

    def _hit_lane(self, arbiter: pymunk.Arbiter, _space: pymunk.Space, _data: dict) -> bool:
        shape = self._other_shape(arbiter)
        lane = next(item for item in self.table.lanes if item.shape is shape)
        if not lane.lit:
            lane.lit = True
            self.hit_events.append("lane")
        return True

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
        for item in [*self.table.bumpers, *self.table.slings, *self.table.targets]:
            item.flash = max(0.0, item.flash - dt)
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
