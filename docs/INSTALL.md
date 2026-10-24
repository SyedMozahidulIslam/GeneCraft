# GeneCraft — Installation Guide

## Requirements

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | 3.11 or 3.12 recommended |
| pygame | 2.5.2 | Core game engine |
| numpy | 1.26.4 | Tile arrays + audio synthesis |
| Disk Space | ~50 MB | Source + saves |
| RAM | 512 MB min | 1 GB recommended for large worlds |

## Installation

### 1. Clone or extract the project
```bash
# From ZIP
unzip GeneCraft_v1.0.0.zip
cd GeneCraft

# From git
git clone https://github.com/yourname/GeneCraft.git
cd GeneCraft
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the game
```bash
python main.py
```

## Platform Notes

### Windows
- Python 3.10+ from [python.org](https://python.org)
- If pygame install fails: `pip install pygame --pre`

### macOS
- Python via Homebrew: `brew install python@3.11`
- May need: `pip install pygame --no-binary pygame`

### Linux (Ubuntu/Debian)
```bash
sudo apt install python3-dev libsdl2-dev
pip install -r requirements.txt
```

## Command-Line Options

```
python main.py [options]

Options:
  --debug        Enable debug mode (verbose logging, FPS counter)
  --fullscreen   Start in fullscreen mode
  --size SIZE    World size: small (100x100), medium (200x200), large (400x400)
  --skip-menu    Skip main menu, jump to sandbox (developer mode)
  --profile      Enable performance profiling output
```

## Verifying Installation

```bash
python -c "import pygame, numpy; print('OK')"
```

Expected output: `OK`

## Troubleshooting

**`ModuleNotFoundError: No module named 'pygame'`**
→ Run `pip install pygame==2.5.2`

**`pygame.error: No available video device`**
→ You are on a headless server. GeneCraft requires a display.

**Low FPS**
→ Try `--size small` for a smaller world, or reduce simulation speed with the 1/2/3/4 keys.

**Save files location**
→ `GeneCraft/saves/` — JSON files, human-readable.

**Log files**
→ `GeneCraft/logs/genecraft.log`
