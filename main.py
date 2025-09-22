# pip install pygame
import pygame
import sys
import random

WIDTH, HEIGHT = 640, 480
CELL = 4
GRID_W, GRID_H = WIDTH // CELL, HEIGHT // CELL
FPS = 60

# --- cell types ---
EMPTY = 0
SAND  = 1
WATER = 2
STEEL = 3
LAVA = 4
STONE = 5

# --- colors ---
COLORS = {
    EMPTY: (20, 20, 25),
    SAND:  (218, 186, 128),
    WATER: (64, 164, 223),
    STEEL: (128, 128, 128),
    LAVA: (255, 69, 0),
    STONE: (100, 100, 100),
}

def make_grid(fill=EMPTY):
    return [[fill for _ in range(GRID_W)] for __ in range(GRID_H)]

def draw_grid(screen, grid):
    for y in range(GRID_H):
        row = grid[y]
        for x in range(GRID_W):
            c = row[x]
            if c != EMPTY:
                pygame.draw.rect(
                    screen, COLORS[c],
                    pygame.Rect(x * CELL, y * CELL, CELL, CELL)
                )

def step_grid(grid):
    next_grid = [row[:] for row in grid]  # copy current grid

    for y in range(GRID_H - 1, -1, -1):
        xs = list(range(GRID_W))
        random.shuffle(xs)  # shuffle update order to prevent gaps
        for x in xs:
            cell = grid[y][x]
            if cell == EMPTY or cell == STEEL:
                continue

            if cell == SAND:
                nx, ny = sand_next_loc(grid, x, y)
            elif cell == WATER:
                nx, ny = liquid_next_loc(grid, x, y, WATER)
                if (nx, ny) != (x, y) and grid[ny][nx] == LAVA:
                    # Water touching lava → turn into stone
                    next_grid[ny][nx] = STONE
                    next_grid[y][x] = EMPTY  # remove the old water
                    continue  # skip rest of logic
            elif cell == LAVA:
                nx, ny = liquid_next_loc(grid, x, y, LAVA)
                if (nx, ny) != (x, y) and grid[ny][nx] == WATER:
                    # Lava touching water → turn into stone
                    next_grid[ny][nx] = STONE
                    next_grid[y][x] = EMPTY  # remove the old lava
                    continue  # skip the rest of the move logic
            elif cell == STONE:
                nx, ny = stone_next_loc(grid, x, y)  # stone falls like sand
            else:
                nx, ny = x, y

            if (nx, ny) != (x, y):
                if next_grid[ny][nx] == EMPTY:
                    next_grid[ny][nx] = cell
                    next_grid[y][x] = EMPTY
                elif cell == STONE and next_grid[ny][nx] == WATER:
                    # Stone sinks into water
                    next_grid[ny][nx] = STONE
                    next_grid[y][x] = WATER
                elif cell == STONE and next_grid[ny][nx] == LAVA:
                    # Stone sinks into water
                    next_grid[ny][nx] = STONE
                    next_grid[y][x] = LAVA
                elif cell == SAND and next_grid[ny][nx] == WATER:
                    # Sand sinks into water
                    next_grid[ny][nx] = SAND
                    next_grid[y][x] = WATER
                elif cell == SAND and next_grid[ny][nx] == LAVA:
                    # Sand sinks into water
                    next_grid[ny][nx] = SAND
                    next_grid[y][x] = LAVA
                else:
                    next_grid[y][x] = cell

    return next_grid


def sand_next_loc(grid, x, y):
    ny = y + 1
    if ny < GRID_H:
        # 1. Fall straight down
        if grid[ny][x] == EMPTY:
            return x, ny
        if grid[ny][x] == WATER:
            return x, ny  # swap handled in step_grid

        # 2. Try diagonals (down-left/right)
        diag = []
        if x > 0:
            if grid[ny][x - 1] == EMPTY or grid[ny][x - 1] == WATER or grid[ny][x - 1] == LAVA:
                diag.append((x - 1, ny))
        if x < GRID_W - 1:
            if grid[ny][x + 1] == EMPTY or grid[ny][x + 1] == WATER or grid[ny][x + 1] == LAVA:
                diag.append((x + 1, ny))
        if diag:
            return random.choice(diag)

    # 3. Stay if nothing else
    return x, y


def water_next_loc(grid, x, y):
    ny = y + 1

    # 1. Fall straight down
    if ny < GRID_H and grid[ny][x] == EMPTY:
        return x, ny

    # 2. Try diagonal down-left/right
    diag = []
    if ny < GRID_H:
        if x > 0 and grid[ny][x - 1] == EMPTY:
            diag.append((x - 1, ny))
        if x < GRID_W - 1 and grid[ny][x + 1] == EMPTY:
            diag.append((x + 1, ny))
    if diag:
        return random.choice(diag)

    # 3. Try sideways (only one step, with dampening)
    sideways = []
    if x > 0 and grid[y][x - 1] == EMPTY:
        sideways.append((x - 1, y))
    if x < GRID_W - 1 and grid[y][x + 1] == EMPTY:
        sideways.append((x + 1, y))
    if sideways and random.random() < 0.5:  # 50% chance to spread
        return random.choice(sideways)

    # 4. Stay in place
    return x, y

def liquid_next_loc(grid, x, y, liquid_type):
    ny = y + 1
    other_liquid = WATER if liquid_type == LAVA else LAVA
    # 1. Fall straight down
    if ny < GRID_H and grid[ny][x] == EMPTY:
        return x, ny

    # 2. Try diagonal down-left/right
    diag = []
    if ny < GRID_H:
        if x > 0 and grid[ny][x - 1] == EMPTY:
            diag.append((x - 1, ny))
        if x < GRID_W - 1 and grid[ny][x + 1] == EMPTY:
            diag.append((x + 1, ny))
        # add option to flow into water
        if x > 0 and grid[ny][x - 1] == other_liquid:
            diag.append((x - 1, ny))
        if x < GRID_W - 1 and grid[ny][x + 1] == other_liquid:
            diag.append((x + 1, ny))
    if diag:
        return random.choice(diag)

    # 3. Try sideways (only one step, with dampening)
    sideways = []
    if x > 0 and grid[y][x - 1] == EMPTY:
        sideways.append((x - 1, y))
    if x < GRID_W - 1 and grid[y][x + 1] == EMPTY:
        sideways.append((x + 1, y))
    # add option to flow into water
    if x > 0 and grid[y][x - 1] == other_liquid:
        sideways.append((x - 1, y))
    if x < GRID_W - 1 and grid[y][x + 1] == other_liquid:
        sideways.append((x + 1, y))
    if sideways and random.random() < 0.5:  # 50% chance to spread
        return random.choice(sideways)

    # 4. Stay in place
    return x, y

def stone_next_loc(grid, x, y):
    ny = y + 1
    if ny < GRID_H:
        if grid[ny][x] == EMPTY or grid[ny][x] == WATER or grid[ny][x] == LAVA:
            return x, ny # stone can fall through water
    return x, y

def draw_at(grid, cell_type, x, y, brush_size):
    for dy in range(-brush_size, brush_size + 1):
        for dx in range(-brush_size, brush_size + 1):
            if dx * dx + dy * dy <= brush_size * brush_size:  # circle brush
                gx, gy = x + dx, y + dy
                if 0 <= gx < GRID_W and 0 <= gy < GRID_H and grid[gy][gx] == EMPTY:
                    grid[gy][gx] = cell_type

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Powder (Grid-Based)")
    clock = pygame.time.Clock()

    grid = make_grid(EMPTY)
    running = True
    dragging = False

    # new controls
    brush_size = 3
    current_cell = SAND
    fast_mode = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // CELL, my // CELL
                draw_at(grid, current_cell, gx, gy, brush_size)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_cell = SAND
                elif event.key == pygame.K_2:
                    current_cell = WATER
                elif event.key == pygame.K_3:
                    current_cell = STEEL
                elif event.key == pygame.K_4:
                    current_cell = LAVA
                elif event.key == pygame.K_5:
                    current_cell = STONE
                elif event.key == pygame.K_LEFTBRACKET:  # shrink brush
                    brush_size = max(1, brush_size - 1)
                elif event.key == pygame.K_RIGHTBRACKET:  # enlarge brush
                    brush_size = min(50, brush_size + 1)
                elif event.key == pygame.K_f:  # toggle fast mode
                    fast_mode = not fast_mode

        # update grid
        steps = 5 if fast_mode else 1
        for _ in range(steps):
            grid = step_grid(grid)

        # draw
        screen.fill(COLORS[EMPTY])
        draw_grid(screen, grid)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
