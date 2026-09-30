"""Physics-backed pinball entities."""

from __future__ import annotations

from dataclasses import dataclass

import pymunk

import settings as S


class Ball:
    """A dynamic pinball body and circle shape."""

    def __init__(self, space: pymunk.Space, position: tuple[float, float]) -> None:
        moment = pymunk.moment_for_circle(S.BALL_MASS, 0, S.BALL_RADIUS)
        self.body = pymunk.Body(S.BALL_MASS, moment)
        self.body.position = position
        self.shape = pymunk.Circle(self.body, S.BALL_RADIUS)
        self.shape.elasticity = S.BALL_ELASTICITY
        self.shape.friction = S.BALL_FRICTION
        self.shape.collision_type = 1
        space.add(self.body, self.shape)

    def cap_speed(self) -> None:
        """Limit velocity to keep collisions stable and play readable."""
        speed = self.body.velocity.length
        if speed > S.MAX_BALL_SPEED:
            self.body.velocity = self.body.velocity.normalized() * S.MAX_BALL_SPEED

    def remove(self, space: pymunk.Space) -> None:
        """Remove the ball from its simulation."""
        if self.body in space.bodies:
            space.remove(self.shape, self.body)


class Flipper:
    """A fast kinematic flipper with explicit angular limits."""

    def __init__(
        self,
        space: pymunk.Space,
        pivot: tuple[float, float],
        rest_angle: float,
        active_angle: float,
        is_left: bool,
    ) -> None:
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = pivot
        self.body.angle = rest_angle
        self.rest_angle = rest_angle
        self.active_angle = active_angle
        self.is_left = is_left
        self.pressed = False
        self.shape = pymunk.Segment(self.body, (0, 0), (S.FLIPPER_LENGTH, 0), S.FLIPPER_RADIUS)
        self.shape.elasticity = S.FLIPPER_ELASTICITY
        self.shape.friction = 0.85
        self.shape.collision_type = 2
        space.add(self.body, self.shape)

    def update(self, dt: float, enabled: bool = True) -> None:
        target = self.active_angle if self.pressed and enabled else self.rest_angle
        speed = S.FLIPPER_SPEED if self.pressed and enabled else S.FLIPPER_RETURN_SPEED
        delta = target - self.body.angle
        move = max(-speed * dt, min(speed * dt, delta))
        self.body.angle += move
        self.body.angular_velocity = move / dt if dt else 0.0

    @property
    def endpoints(self) -> tuple[tuple[float, float], tuple[float, float]]:
        start = tuple(self.body.position)
        end = tuple(self.body.local_to_world((S.FLIPPER_LENGTH, 0)))
        return start, end


class Plunger:
    """Chargeable spring launcher state."""

    def __init__(self) -> None:
        self.held = False
        self.charge = 0.0

    def update(self, dt: float) -> None:
        if self.held:
            self.charge = min(S.PLUNGER_MAX_HOLD, self.charge + dt)

    @property
    def power(self) -> float:
        return self.charge / S.PLUNGER_MAX_HOLD

    def release_impulse(self) -> float:
        power = self.power
        self.charge = 0.0
        self.held = False
        return S.PLUNGER_MIN_IMPULSE + (S.PLUNGER_MAX_IMPULSE - S.PLUNGER_MIN_IMPULSE) * power


@dataclass
class Bumper:
    position: tuple[float, float]
    color: tuple[int, int, int]
    shape: pymunk.Shape
    flash: float = 0.0


@dataclass
class Slingshot:
    points: tuple[tuple[int, int], ...]
    kick: tuple[float, float]
    shape: pymunk.Shape
    flash: float = 0.0


@dataclass
class Target:
    start: tuple[int, int]
    end: tuple[int, int]
    shape: pymunk.Shape
    down: bool = False
    flash: float = 0.0


@dataclass
class Lane:
    x: int
    label: str
    shape: pymunk.Shape
    lit: bool = False
