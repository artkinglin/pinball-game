"""Main game state and update loop."""

from __future__ import annotations

import json
from pathlib import Path

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
        self.score = 0
        self.balls_remaining = S.STARTING_BALLS
        self.extra_ball_awarded = False
        self.tilted = False
        self.nudge_times: list[float] = []
        self.elapsed = 0.0
        self.serve_timer = 0.0
        self.target_reset_timer = 0.0
        self.game_over = False
        self.high_score_path = Path(__file__).with_name(S.HIGH_SCORE_FILE)
        self.high_score = self._load_high_score()

    def _setup_collisions(self) -> None:
        self.space.on_collision(1, 3, begin=self._hit_bumper)
        self.space.on_collision(1, 4, begin=self._hit_sling)
        self.space.on_collision(1, 5, begin=self._hit_target)
        self.space.on_collision(1, 6, begin=self._hit_lane)

    @staticmethod
    def _other_shape(arbiter: pymunk.Arbiter) -> pymunk.Shape:
        return next(shape for shape in arbiter.shapes if shape.collision_type != 1)

    def _load_high_score(self) -> int:
        try:
            return int(json.loads(self.high_score_path.read_text(encoding="utf-8")).get("high_score", 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return 0

    def _save_high_score(self) -> None:
        try:
            self.high_score_path.write_text(json.dumps({"high_score": self.high_score}, indent=2), encoding="utf-8")
        except OSError:
            pass

    def add_score(self, points: int) -> None:
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
        if self.score >= S.EXTRA_BALL_SCORE and not self.extra_ball_awarded:
            self.balls_remaining += 1
            self.extra_ball_awarded = True

    def restart(self) -> None:
        self.ball.remove(self.space)
        self.ball = Ball(self.space, S.PLUNGER_SPAWN)
        self.score = 0
        self.balls_remaining = S.STARTING_BALLS
        self.extra_ball_awarded = False
        self.tilted = False
        self.nudge_times.clear()
        self.serve_timer = 0.0
        self.target_reset_timer = 0.0
        self.game_over = False
        self.hit_events.clear()
        for target in self.table.targets:
            target.down = False
            target.shape.sensor = False
        for lane in self.table.lanes:
            lane.lit = False

    def _drain_ball(self) -> None:
        self.ball.remove(self.space)
        self.tilted = False
        self.nudge_times.clear()
        if self.balls_remaining > 1:
            self.balls_remaining -= 1
            self.serve_timer = S.SERVE_DELAY
        else:
            self.balls_remaining = 0
            self.game_over = True
            self._save_high_score()

    def _serve_ball(self) -> None:
        self.ball = Ball(self.space, S.PLUNGER_SPAWN)
        self.serve_timer = 0.0

    def _nudge(self) -> None:
        if self.game_over or self.serve_timer > 0:
            return
        self.nudge_times = [stamp for stamp in self.nudge_times if self.elapsed - stamp <= S.NUDGE_WINDOW]
        self.nudge_times.append(self.elapsed)
        if len(self.nudge_times) >= S.NUDGE_LIMIT:
            self.tilted = True
            return
        direction = -1 if len(self.nudge_times) % 2 else 1
        self.ball.body.apply_impulse_at_local_point((direction * S.NUDGE_IMPULSE, -S.NUDGE_IMPULSE * 0.35))

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
            if event.key == pygame.K_r:
                self.restart()
            if event.key == pygame.K_RETURN and self.game_over:
                self.restart()
            if event.key == pygame.K_n:
                self._nudge()
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
        self.elapsed += dt
        self.left_flipper.update(dt, not self.tilted)
        self.right_flipper.update(dt, not self.tilted)
        self.plunger.update(dt)
        for item in [*self.table.bumpers, *self.table.slings, *self.table.targets]:
            item.flash = max(0.0, item.flash - dt)
        self._process_hit_events()
        if self.target_reset_timer > 0:
            self.target_reset_timer -= dt
            if self.target_reset_timer <= 0:
                for target in self.table.targets:
                    target.down = False
                    target.shape.sensor = False
        if self.game_over:
            return
        if self.serve_timer > 0:
            self.serve_timer -= dt
            if self.serve_timer <= 0:
                self._serve_ball()
            return
        step = S.FIXED_DT / S.PHYSICS_SUBSTEPS
        for _ in range(S.PHYSICS_SUBSTEPS):
            self.space.step(step)
            self.ball.cap_speed()
        if self.ball.body.position.y > S.DRAIN_Y:
            self._drain_ball()

    def _process_hit_events(self) -> None:
        values = {
            "bumper": S.BUMPER_SCORE,
            "sling": S.SLING_SCORE,
            "target": S.TARGET_SCORE,
            "lane": S.LANE_SCORE,
        }
        while self.hit_events:
            self.add_score(values[self.hit_events.pop(0)])
        if self.target_reset_timer <= 0 and self.table.targets and all(target.down for target in self.table.targets):
            self.add_score(S.CLEAR_BONUS * 2)
            self.target_reset_timer = S.TARGET_RESET_DELAY
        if self.table.lanes and all(lane.lit for lane in self.table.lanes):
            for lane in self.table.lanes:
                lane.lit = False

    def draw(self) -> None:
        self.screen.fill(S.BLACK)
        draw_table(self.screen, self.table)
        draw_flipper(self.screen, self.left_flipper)
        draw_flipper(self.screen, self.right_flipper)
        draw_plunger(self.screen, self.plunger.power)
        if not self.game_over and self.serve_timer <= 0:
            draw_ball(self.screen, tuple(self.ball.body.position), self.crt)
        draw_text(self.screen, self.title_font, "NEON PINBALL", (S.WIDTH // 2, 24), S.MAGENTA, center=True)
        draw_text(self.screen, self.hud_font, f"SCORE {self.score:08d}", (S.HUD_MARGIN, 48), S.GREEN)
        draw_text(self.screen, self.hud_font, f"BALLS {self.balls_remaining}", (S.WIDTH - 125, 48), S.YELLOW)
        draw_text(self.screen, self.hud_font, f"HI {self.high_score:08d}", (S.HUD_MARGIN, S.HEIGHT - 27), S.CYAN)
        for lane in self.table.lanes:
            draw_text(self.screen, self.hud_font, lane.label, (lane.x, 88), S.GREEN if lane.lit else S.WHITE, center=True)
        if self.tilted:
            draw_text(self.screen, self.title_font, "TILT", (S.WIDTH // 2, 430), S.RED, center=True)
        if self.serve_timer > 0:
            draw_text(self.screen, self.title_font, "BALL DRAINED", (S.WIDTH // 2, 430), S.MAGENTA, center=True)
        if self.game_over:
            draw_text(self.screen, self.title_font, "GAME OVER", (S.WIDTH // 2, 405), S.MAGENTA, center=True)
            draw_text(self.screen, self.hud_font, f"FINAL {self.score:08d}", (S.WIDTH // 2, 448), S.WHITE, center=True)
            draw_text(self.screen, self.hud_font, "PRESS ENTER", (S.WIDTH // 2, 480), S.YELLOW, center=True)
        if self.paused:
            draw_text(self.screen, self.title_font, "PAUSED", (S.WIDTH // 2, S.HEIGHT // 2), S.YELLOW, center=True)
