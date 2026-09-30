"""Executable entry point for Neon Pinball."""

from __future__ import annotations

import argparse
import os


def run(smoke_frames: int = 0) -> None:
    """Run the fixed-timestep pygame loop."""
    if smoke_frames:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame

    import settings as S
    from game import Game

    pygame.mixer.pre_init(S.SAMPLE_RATE, size=-16, channels=S.AUDIO_CHANNELS, buffer=S.AUDIO_BUFFER)
    pygame.init()
    pygame.display.set_caption("Neon Pinball")
    screen = pygame.display.set_mode((S.WIDTH, S.HEIGHT))
    clock = pygame.time.Clock()
    game = Game(screen)
    running = True
    frame = 0
    accumulator = 0.0
    while running:
        frame_time = min(clock.tick(S.FPS) / 1000.0, 0.1)
        accumulator += frame_time
        for event in pygame.event.get():
            running = game.handle_event(event)
        while accumulator >= S.FIXED_DT:
            game.update(S.FIXED_DT)
            accumulator -= S.FIXED_DT
        game.draw()
        pygame.display.flip()
        frame += 1
        if smoke_frames and frame >= smoke_frames:
            running = False
    pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Neon arcade pinball")
    parser.add_argument("--smoke-frames", type=int, default=0, help=argparse.SUPPRESS)
    args = parser.parse_args()
    run(args.smoke_frames)
