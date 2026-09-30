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
