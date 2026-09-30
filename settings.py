"""Shared game and physics constants."""

from __future__ import annotations

WIDTH = 600
HEIGHT = 900
FPS = 60
FIXED_DT = 1.0 / FPS
PHYSICS_SUBSTEPS = 4

BLACK = (0, 0, 0)
CYAN = (0, 245, 255)
MAGENTA = (255, 45, 210)
YELLOW = (255, 230, 40)
GREEN = (40, 255, 110)
WHITE = (245, 245, 255)
DIM_CYAN = (0, 75, 85)
RED = (255, 55, 70)

GRAVITY = 620.0
BALL_RADIUS = 10
BALL_MASS = 1.0
BALL_ELASTICITY = 0.72
BALL_FRICTION = 0.25
MAX_BALL_SPEED = 1050.0

WALL_RADIUS = 5
WALL_ELASTICITY = 0.58
WALL_FRICTION = 0.32
TABLE_LEFT = 42
TABLE_RIGHT = 558
TABLE_TOP = 74
TABLE_BOTTOM = 850
PLUNGER_LANE_X = 523
PLUNGER_SPAWN = (522.0, 790.0)

FLIPPER_LENGTH = 112
FLIPPER_RADIUS = 10
FLIPPER_SPEED = 13.0
FLIPPER_RETURN_SPEED = 9.0
FLIPPER_ELASTICITY = 0.45
LEFT_FLIPPER_PIVOT = (205.0, 742.0)
RIGHT_FLIPPER_PIVOT = (395.0, 742.0)
LEFT_FLIPPER_REST = 0.34
LEFT_FLIPPER_ACTIVE = -0.47
RIGHT_FLIPPER_REST = 2.80
RIGHT_FLIPPER_ACTIVE = 3.61

PLUNGER_MAX_HOLD = 1.5
PLUNGER_MIN_IMPULSE = 480.0
PLUNGER_MAX_IMPULSE = 1120.0

BUMPER_RADIUS = 31
BUMPER_IMPULSE = 455.0
SLING_IMPULSE = 330.0
NUDGE_IMPULSE = 105.0
NUDGE_WINDOW = 5.0
NUDGE_LIMIT = 3
FLASH_TIME = 0.13
TARGET_RESET_DELAY = 1.2
DRAIN_Y = 875

BUMPER_SCORE = 100
SLING_SCORE = 10
TARGET_SCORE = 500
LANE_SCORE = 250
CLEAR_BONUS = 2000
EXTRA_BALL_SCORE = 10_000
STARTING_BALLS = 3
SERVE_DELAY = 1.15
HIGH_SCORE_FILE = "highscore.json"

MASTER_VOLUMES = (0.0, 0.22, 0.45, 0.7)
SAMPLE_RATE = 44_100
AUDIO_CHANNELS = 2
AUDIO_BUFFER = 512
DEFAULT_VOLUME_INDEX = 2
SOUND_SPECS = {
    "flipper": (155.0, 0.045, "noise"),
    "bumper": (720.0, 0.12, "square"),
    "launch": (220.0, 0.22, "riser"),
    "target": (980.0, 0.09, "square"),
    "sling": (430.0, 0.07, "triangle"),
    "lane": (1120.0, 0.07, "triangle"),
    "drain": (185.0, 0.36, "faller"),
    "game_over": (105.0, 0.65, "faller"),
}

HUD_MARGIN = 18
SCANLINE_ALPHA = 22
GLOW_LAYERS = 3

# Physics layout lives in one editable data structure.
TABLE_LAYOUT = {
    "bumpers": [
        {"position": (205, 235), "color": CYAN},
        {"position": (300, 178), "color": MAGENTA},
        {"position": (395, 235), "color": YELLOW},
    ],
    "slings": [
        {"points": ((118, 650), (175, 698), (112, 712)), "kick": (235, -245)},
        {"points": ((482, 650), (425, 698), (488, 712)), "kick": (-235, -245)},
    ],
    "targets": [
        {"a": (212, 347), "b": (245, 342)},
        {"a": (284, 335), "b": (316, 335)},
        {"a": (355, 342), "b": (388, 347)},
    ],
    "lanes": [
        {"x": 165, "label": "A"},
        {"x": 245, "label": "R"},
        {"x": 325, "label": "C"},
        {"x": 405, "label": "D"},
    ],
}
