# Dungeons of PPY

A standalone, text-based fantasy RPG built in Python. Explore an endless dungeon, fight enemies, manage inventory, and save your progress — all from the terminal.

Created as a Python final project. The codebase demonstrates modules, OOP, decorators, generators, comprehensions, regex, JSON persistence, and custom exceptions.

## Features

- **Endless dungeon** — random rooms via a generator (empty halls, traps, loot, enemies)
- **Turn-based combat** — attack or use items; numbered shortcuts or `attack` / `use` commands (regex-parsed)
- **Items** — potions, equippable weapons, readable books with permanent bonuses
- **Inventory** — equip weapons, use consumables, view item descriptions
- **Save system** — multiple JSON save slots (create, load, delete)
- **Game over** — death from traps or combat; restart or quit
- **Terminal UI** — ANSI colors and optional typewriter animation

## Requirements

- **Python 3.10+** (3.x works)
- No third-party packages — standard library only
- A terminal that supports **ANSI colors** (Windows Terminal, PowerShell, WSL, Linux, macOS)

## How to run

1. Clone or unzip the project folder.
2. Open a terminal in the project directory.
3. Run:

   ```bash
   python main.py
   ```

On first run, a `saves/` folder is created automatically for JSON save files.

## How to play

### Startup

- If save files exist, you can load one or start a new game.
- You may skip or watch the intro story.

### Main menu

| Option | Action |
|--------|--------|
| 1 | Explore the dungeon (next random encounter) |
| 2 | Open inventory |
| 3 | Settings (toggle text animation, replay intro) |
| 4 | Save game |
| 5 | Load game |
| 6 | Delete save |
| 7 | New game |
| 8 | Quit |

### Exploring

- **Empty room** — safe passage
- **Trap** — take damage (lethal at 0 HP)
- **Chest** — add items to inventory
- **Enemy** — enter combat

### Combat

- Choose a numbered action, or type commands such as `attack Goblin` or `use Health Potion`.
- Invalid commands show a clear error message.
- Defeating an enemy grants XP. Temporary buffs reset after each fight.

### Inventory

- Select an item by number to use or equip it (weapons, potions, books).
- Equipped weapons are marked `[EQUIPPED]`.

### Death

- If you die from a trap or in combat, you can **start a new adventure** or **quit**.

## Project structure

| File | Role |
|------|------|
| `main.py` | Entry point, main menu, explore flow, inventory, game over |
| `engine.py` | Screen clearing, colors, HUD, `@typewriter` decorator, intro |
| `entities.py` | `Character`, `Player`, `Enemy` |
| `world.py` | `encounter_generator()` — endless dungeon events |
| `combat.py` | Combat loop, regex command parser, `InvalidCombatActionError` |
| `item_manager.py` | `Item` hierarchy, registry, `apply_item()` |
| `save_manager.py` | JSON save/load/delete, `SaveDataError`, startup load prompt |

## Notes

- **Saves** are generated at runtime under `saves/*.json` and excluded from version control.
- **Animation** — when enabled, story text uses a typewriter effect; turn it off in Settings for faster menus.
- **Attack power** — shown value = base stats + temporary combat buffs; saves store base stats only.

## Project Background

I created this project independently as my first-year Python final project at
the Polish-Japanese Academy of Information Technology. It demonstrates my use
of Python fundamentals, object-oriented design, modular code organization,
input validation, procedural generation, and JSON persistence.

## License

This project is licensed under the [MIT License](LICENSE).
