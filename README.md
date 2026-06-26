# 🧩 2D Maze Game

A fun and challenging maze game built with Python and Pygame. Navigate through procedurally generated mazes, race against the clock, and compete for the top spot on the leaderboard!

---

## ✨ Features

### 🎮 Gameplay
- **Procedurally generated mazes** — every game is a unique maze, no two runs are the same
- **3 difficulty levels** — Easy, Medium, and Hard with increasing maze sizes
- **Arrow key controls** — simple and responsive movement
- **Collision limit** — hit 3 walls and it's game over, so plan your path carefully!

### 🎨 Visuals
- **Road-textured paths** — grey tarmac with white dashed centre-lines (horizontal, vertical, and crossing variants)
- **Grass & tree walls** — lush green walls with randomised grass texture and tree clusters
- **Smooth popup overlays** — rounded modal dialogs for win, game over, and highscores
- **Live stats panel** — tracks your time, moves, and wall hits in real time

### 🏆 Scoring & Leaderboard
- **Persistent highscores** — scores saved to `highscores.json` across sessions
- **Per-difficulty leaderboards** — separate top-10 tables for Easy, Medium, and Hard
- **New highscore detection** — a special badge appears on the win screen if you set a new record
- **Sorted by time** — fastest time wins, with collision count as a tie-breaker

### 🔔 Popups & Screens
- **Game Over popup** — triggered after 3 wall collisions, with Restart and Main Menu options
- **Win popup** — shows your final time, hits, and a ★ New Highscore badge if earned
- **Highscore table screen** — viewable anytime via the panel button or `H` key
- **Main Menu** — enter your name and pick a difficulty before each run

### 🔊 Sound Effects
- **Collision sound** — plays on every wall hit
- **Victory sound** — plays when you reach the goal
- **Auto-fallback** — if `.wav` files are missing, the game generates beep sounds automatically

---

## 🚀 Getting Started

### Requirements
- Python 3.8+
- Pygame 2.1+

### Installation

```bash
# Clone or download the project folder, then:
pip install -r requirements.txt
```

### Run the Game

```bash
python main.py
```

---

## 🕹️ Controls

| Key | Action |
|-----|--------|
| ↑ ↓ ← → | Move the player |
| `R` | Restart the current maze |
| `H` | Open the Highscores screen |
| `Q` | Quit to Main Menu |

---

## 📁 Project Structure

```
2D Maze Game/
│
├── main.py              # Entry point — initialises pygame and runs the game loop
├── menu.py              # Main menu screen (name input, difficulty selection)
├── game.py              # Core game logic, rendering, and all popup screens
├── maze_generator.py    # Recursive-backtracker maze generation algorithm
├── player.py            # Player state (position, moves, collisions)
├── leaderboard.py       # Load/save/query scores from highscores.json
├── sounds.py            # Sound loader with generated fallback beeps
├── settings.py          # All constants (colours, grid sizes, FPS, limits)
├── highscores.json      # Auto-created on first win
├── requirements.txt     # Python dependencies
│
└── assets/
    ├── collision.wav    # (optional) Wall hit sound effect
    └── victory.wav      # (optional) Win sound effect
```

---

## 🧠 How It Works

The maze is generated using the **recursive backtracker algorithm** (a depth-first search), which guarantees:
- Every maze is fully solvable
- There is exactly one path between any two cells
- The layout is different every time you play

The player starts at the **top-left** of the maze and must reach the **green ★ goal** at the bottom-right.

---

## 📸 Difficulty Overview

| Difficulty | Grid Size | Cell Size |
|------------|-----------|-----------|
| Easy       | 11 × 11   | 48 px     |
| Medium     | 17 × 17   | 36 px     |
| Hard       | 25 × 25   | 26 px     |

---

## 📝 License

Free to use and modify for personal or educational projects.
