"""Procedurally generated chiptune sound effects."""

from __future__ import annotations

import numpy as np
import pygame

import settings as S


class AudioManager:
    """Builds short waveforms in memory; no external assets required."""

    def __init__(self) -> None:
        self.volume_index = S.DEFAULT_VOLUME_INDEX
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.available = pygame.mixer.get_init() is not None
        if self.available:
            for name, spec in S.SOUND_SPECS.items():
                self.sounds[name] = self._make_sound(*spec)
            self._apply_volume()

    def _make_sound(self, frequency: float, duration: float, wave: str) -> pygame.mixer.Sound:
        count = max(1, int(S.SAMPLE_RATE * duration))
        sweep = np.ones(count)
        if wave == "riser":
            sweep = np.linspace(1.0, 2.1, count)
        elif wave == "faller":
            sweep = np.linspace(1.0, 0.42, count)
        phase = 2.0 * np.pi * frequency * np.cumsum(sweep) / S.SAMPLE_RATE
        if wave == "noise":
            values = np.random.default_rng(7).uniform(-1.0, 1.0, count)
        elif wave in ("square", "riser", "faller"):
            values = np.sign(np.sin(phase))
        else:
            values = (2.0 / np.pi) * np.arcsin(np.sin(phase))
        envelope = np.linspace(1.0, 0.0, count) ** 1.7
        mono = np.asarray(values * envelope * 22_000, dtype=np.int16)
        stereo = np.column_stack((mono, mono))
        return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))

    def _apply_volume(self) -> None:
        volume = S.MASTER_VOLUMES[self.volume_index]
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def play(self, name: str) -> None:
        if self.available and name in self.sounds:
            self.sounds[name].play()

    def cycle_volume(self) -> None:
        self.volume_index = (self.volume_index + 1) % len(S.MASTER_VOLUMES)
        self._apply_volume()

    @property
    def volume_percent(self) -> int:
        return round(S.MASTER_VOLUMES[self.volume_index] * 100)
