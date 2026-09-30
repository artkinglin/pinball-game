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


def draw_table(surface: pygame.Surface, table: object) -> None:
    """Draw the initial neon table outlines."""
    for wall in table.walls:
        pygame.draw.line(surface, S.CYAN, wall.a, wall.b, 2)
    pygame.draw.line(surface, S.MAGENTA, (S.PLUNGER_LANE_X - 22, 345), (S.PLUNGER_LANE_X - 22, S.TABLE_BOTTOM), 2)


def draw_scanlines(surface: pygame.Surface) -> None:
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for y in range(0, S.HEIGHT, 4):
        pygame.draw.line(overlay, (0, 0, 0, S.SCANLINE_ALPHA), (0, y), (S.WIDTH, y))
    surface.blit(overlay, (0, 0))
