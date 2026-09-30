"""Neon vector rendering helpers."""

from __future__ import annotations

import pygame

import settings as S


def pixel_font(size: int) -> pygame.font.Font:
    """Return a bundled monospace-like font for crisp retro text."""
    return pygame.font.Font(pygame.font.match_font("consolas,couriernew,monospace"), size)


def draw_text(surface: pygame.Surface, font: pygame.font.Font, text: str, pos: tuple[int, int], color: tuple[int, int, int], center: bool = False) -> None:
    image = font.render(text, False, color)
    rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
    surface.blit(image, rect)


def draw_table(surface: pygame.Surface, table: object, glow: bool = True) -> None:
    """Draw the initial neon table outlines."""
    glow_layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for wall in table.walls:
        if glow:
            pygame.draw.line(glow_layer, (*S.CYAN, 28), wall.a, wall.b, 9)
        pygame.draw.line(surface, S.CYAN, wall.a, wall.b, 2)
    pygame.draw.line(surface, S.MAGENTA, (S.PLUNGER_LANE_X - 22, 345), (S.PLUNGER_LANE_X - 22, S.TABLE_BOTTOM), 2)
    for bumper in table.bumpers:
        position = tuple(map(round, bumper.position))
        if glow:
            pygame.draw.circle(glow_layer, (*bumper.color, 25), position, S.BUMPER_RADIUS + 12)
        if bumper.flash > 0:
            pygame.draw.circle(surface, bumper.color, position, S.BUMPER_RADIUS + 10, 2)
        pygame.draw.circle(surface, bumper.color, position, S.BUMPER_RADIUS, 3)
        pygame.draw.circle(surface, S.WHITE, position, S.BUMPER_RADIUS - 8, 1)
        pygame.draw.circle(surface, bumper.color, position, 5)
    for sling in table.slings:
        color = S.WHITE if sling.flash > 0 else S.MAGENTA
        pygame.draw.polygon(surface, color, sling.points, 3)
    for target in table.targets:
        color = S.DIM_CYAN if target.down else S.YELLOW
        width = 1 if target.down else 6
        pygame.draw.line(surface, color, target.start, target.end, width)
    for lane in table.lanes:
        color = S.GREEN if lane.lit else S.CYAN
        pygame.draw.line(surface, color, (lane.x - 20, 112), (lane.x + 20, 112), 2)
    if glow:
        surface.blit(glow_layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def draw_ball(surface: pygame.Surface, position: tuple[float, float], glow: bool) -> None:
    point = (round(position[0]), round(position[1]))
    if glow:
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for radius, alpha in ((24, 22), (18, 35), (14, 55)):
            pygame.draw.circle(layer, (*S.CYAN, alpha), point, radius)
        surface.blit(layer, (0, 0))
    pygame.draw.circle(surface, S.WHITE, point, S.BALL_RADIUS)
    pygame.draw.circle(surface, S.CYAN, point, S.BALL_RADIUS, 2)
    pygame.draw.circle(surface, S.WHITE, (point[0] - 3, point[1] - 3), 2)


def draw_flipper(surface: pygame.Surface, flipper: object) -> None:
    start, end = flipper.endpoints
    pygame.draw.line(surface, S.MAGENTA, start, end, S.FLIPPER_RADIUS * 2)
    pygame.draw.line(surface, S.WHITE, start, end, 2)
    pygame.draw.circle(surface, S.YELLOW, start, S.FLIPPER_RADIUS + 3, 2)


def draw_plunger(surface: pygame.Surface, power: float) -> None:
    base_y = 830
    pygame.draw.line(surface, S.YELLOW, (S.PLUNGER_LANE_X, base_y), (S.PLUNGER_LANE_X, base_y - 35 + int(22 * power)), 5)
    pygame.draw.rect(surface, S.WHITE, (S.PLUNGER_LANE_X - 13, base_y, 26, 7), 2)
    meter = pygame.Rect(S.WIDTH - 24, 510, 8, 180)
    pygame.draw.rect(surface, S.DIM_CYAN, meter, 1)
    fill = int(meter.height * power)
    if fill:
        pygame.draw.rect(surface, S.YELLOW, (meter.x + 2, meter.bottom - fill, meter.width - 4, fill))


def draw_scanlines(surface: pygame.Surface) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for y in range(0, S.HEIGHT, 4):
        pygame.draw.line(overlay, (0, 0, 0, S.SCANLINE_ALPHA), (0, y), (S.WIDTH, y))
    surface.blit(overlay, (0, 0))
