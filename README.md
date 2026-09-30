# Neon Pinball

A complete code-drawn retro arcade table built with pygame-ce (the maintained pygame distribution) and pymunk. It uses no image or audio assets: every neon line is a pygame primitive and every chiptune sound is synthesized at startup.

## Run

```powershell
python -m pip install -r requirements.txt
python main.py
```

Python 3.10+ is recommended. On Windows with Python 3.14, `pygame-ce` supplies the compatible `pygame` module.

## Controls

| Key | Action |
| --- | --- |
| Left Shift / Left Arrow | Left flipper |
| Right Shift / Right Arrow | Right flipper |
| Space (hold/release) | Charge and fire plunger |
| N | Nudge (three within five seconds causes TILT) |
| C | Toggle CRT scanlines and glow |
| M | Cycle mute/low/medium/high volume |
| P | Pause |
| R | Restart game |
| Escape | Quit |
| Enter | New game after game over |

You begin with three balls. Bumpers score 100, slingshots 10, drop targets 500, and rollover lanes 250. Clearing all targets awards a 4,000-point doubled bonus. Reach 10,000 for one extra ball. The high score is stored locally in `highscore.json`.

## Tuning and layout

All gameplay constants are collected in `settings.py`:

- `GRAVITY` changes the table slope. Higher values make the ball drain faster.
- `BALL_ELASTICITY` controls ball bounciness.
- `FLIPPER_SPEED` controls the powered snap; `FLIPPER_RETURN_SPEED` controls release speed.
- `BUMPER_IMPULSE`, `SLING_IMPULSE`, and the plunger impulse range control kick strength.
- `MAX_BALL_SPEED` is the safety cap used with the fixed timestep and four physics substeps.
- `TABLE_LAYOUT` contains bumper, slingshot, target, and lane positions for quick edits.

For a quick non-interactive launch check, run `python main.py --smoke-frames 10`.

## Project structure

- `main.py` — startup and fixed-timestep loop
- `game.py` — game state, input, scoring, tilt, and ball lifecycle
- `table.py` — table geometry and physics objects
- `entities.py` — balls, flippers, plunger, and feature data
- `audio.py` — procedural square/triangle/noise effects
- `render.py` — vector drawing, glow, text, and CRT scanlines
- `settings.py` — editable constants and layout configuration
