"""Editable table layout and static physics geometry."""

from __future__ import annotations

import math

import pymunk

import settings as S
from entities import Bumper, Lane, Slingshot, Target


class Table:
    """Constructs the playfield geometry from settings.TABLE_LAYOUT."""

    def __init__(self, space: pymunk.Space) -> None:
        self.space = space
        self.walls: list[pymunk.Segment] = []
        self.bumpers: list[Bumper] = []
        self.slings: list[Slingshot] = []
        self.targets: list[Target] = []
        self.lanes: list[Lane] = []
        self._build_walls()
        self._build_features()

    def _segment(self, a: tuple[float, float], b: tuple[float, float], radius: int = S.WALL_RADIUS) -> pymunk.Segment:
        shape = pymunk.Segment(self.space.static_body, a, b, radius)
        shape.elasticity = S.WALL_ELASTICITY
        shape.friction = S.WALL_FRICTION
        self.space.add(shape)
        self.walls.append(shape)
        return shape

    def _build_walls(self) -> None:
        left, right, top, bottom = S.TABLE_LEFT, S.TABLE_RIGHT, S.TABLE_TOP, S.TABLE_BOTTOM
        self._segment((left, 205), (left, bottom))
        self._segment((right, 205), (right, bottom))
        # Faceted semicircle behaves like a smooth arch with no image assets.
        center = (300, 205)
        radius = right - center[0]
        points = []
        for index in range(17):
            angle = math.pi + (math.pi * index / 16)
            points.append((center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle)))
        for a, b in zip(points, points[1:]):
            self._segment(a, b)
        self._segment((left, bottom), (170, bottom))
        self._segment((430, bottom), (right, bottom))
        self._segment((S.PLUNGER_LANE_X - 22, 345), (S.PLUNGER_LANE_X - 22, bottom))
        self._segment((68, 555), (120, 684))
        self._segment((532, 555), (480, 684))
        self._segment((120, 684), (174, 727))
        self._segment((480, 684), (426, 727))

    def _build_features(self) -> None:
        for item in S.TABLE_LAYOUT["bumpers"]:
            shape = pymunk.Circle(self.space.static_body, S.BUMPER_RADIUS, item["position"])
            shape.elasticity = 1.0
            shape.collision_type = 3
            self.space.add(shape)
            self.bumpers.append(Bumper(item["position"], item["color"], shape))
        for item in S.TABLE_LAYOUT["slings"]:
            a, b, c = item["points"]
            shape = pymunk.Poly(self.space.static_body, (a, b, c))
            shape.elasticity = 0.9
            shape.collision_type = 4
            self.space.add(shape)
            self.slings.append(Slingshot(item["points"], item["kick"], shape))
        for item in S.TABLE_LAYOUT["targets"]:
            shape = pymunk.Segment(self.space.static_body, item["a"], item["b"], 5)
            shape.elasticity = 0.4
            shape.collision_type = 5
            self.space.add(shape)
            self.targets.append(Target(item["a"], item["b"], shape))
        for item in S.TABLE_LAYOUT["lanes"]:
            shape = pymunk.Segment(self.space.static_body, (item["x"] - 18, 113), (item["x"] + 18, 113), 1)
            shape.sensor = True
            shape.collision_type = 6
            self.space.add(shape)
            self.lanes.append(Lane(item["x"], item["label"], shape))
