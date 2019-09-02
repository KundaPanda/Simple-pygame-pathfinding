import pygame, pygame.gfxdraw
import heapq
from enum import Enum

#TODO: comments, fix diagonal walls with 1 thickness

DEBUG = True
MAX_TPS = 50000

size = width, height = 1131, 569
bottom_bar_height = 40
cell_size = 10
font_renderer, bottom_bar_font = None, None
max_row = (height - bottom_bar_height) // cell_size
max_col = width // cell_size
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
playground = None
clock = pygame.time.Clock()
x, y = 0, 0
wall_radius = 5
update_counter = 40
should_update = True


class Fill(Enum):
    FREE = 0
    TARGET = 1
    START = 2
    PATH = 3
    WALL = 4


class Cell:
    def __init__(self):
        self.fill = Fill.FREE
        self.distance = None
        self.pushed = False
        self.x = 0
        self.y = 0
        self.reachable = 0


class Color(Enum):
    WHITE = (255, 255, 255)
    YELLOW = (252, 233, 3)
    BLACK = (0, 0, 0)
    RED = (233, 56, 56)
    BLUE = (32, 27, 175)
    ORANGE = (255, 140, 5)
    GREEN = (15, 226, 21)


def init():
    global font_renderer, bottom_bar_font
    pygame.init()
    pygame.font.init()
    font_renderer = pygame.font.SysFont('Arial', cell_size - (cell_size // 4))
    bottom_bar_font = pygame.font.SysFont('Arial', int(bottom_bar_height * 0.8))
    grid_init()
    # pygame.display.flip()


def grid_init():
    global playground, screen, height, width, size, bottom_bar_height
    screen.fill(Color.BLACK.value)
    if (width % cell_size) != 0:
        width = width - (width % cell_size)
    if (height % cell_size) != 0:
        height = height - (height % cell_size)
    size = width, height
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    playground = [[Cell() for _ in range(width // cell_size)] for _ in range((height) // cell_size)]
    for arow in range(0, height - bottom_bar_height, cell_size):
        for col in range(0, width, cell_size):
            print(arow)
            playground[arow // cell_size][col // cell_size].x = col // cell_size
            playground[arow // cell_size][col // cell_size].y = arow // cell_size
            pygame.gfxdraw.rectangle(screen, (col, arow, cell_size, cell_size), Color.WHITE.value)
    update_info()


def update_info():
    global bottom_bar_font, bottom_bar_height, screen
    w_radius = bottom_bar_font.render("Wall size: %d" % (wall_radius), False, Color.WHITE.value)
    screen.blit(w_radius, (20, max_row * cell_size + (0.1 * bottom_bar_height)))
    pygame.display.update()


def finish(path):
    for column, row in path:
        playground[row][column].fill = Fill.PATH
        pygame.gfxdraw.box(screen, (column * cell_size, row * cell_size, cell_size, cell_size), Color.BLUE.value)
        pygame.display.update()
        clock.tick(MAX_TPS)


def idle():
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit(0)
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT, dict()))
        pygame.display.update()
        clock.tick(MAX_TPS)


placed = {
    "target": False,
    "start": False
}
started = False
q = []

init()
while True:
    left_pressed, middle_pressed, right_pressed = pygame.mouse.get_pressed()
    x, y = pygame.mouse.get_pos()
    x = (x // cell_size) * cell_size
    y = (y // cell_size) * cell_size
    if not started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
            elif middle_pressed and not placed["target"]:
                coords = x // cell_size, y // cell_size
                if playground[coords[1]][coords[0]].fill != Fill.FREE:
                    continue
                pygame.gfxdraw.box(screen, (x, y, cell_size, cell_size), Color.RED.value)
                placed["target"] = coords
                playground[coords[1]][coords[0]].fill = Fill.TARGET
                print("Placed target at: x={} y={} ({})".format(x, y, placed))
            elif left_pressed and not placed["start"]:
                coords = x // cell_size, y // cell_size
                if playground[coords[1]][coords[0]].fill != Fill.FREE:
                    continue
                playground[coords[1]][coords[0]].fill = Fill.START
                placed["start"] = coords
                pygame.gfxdraw.box(screen, (x, y, cell_size, cell_size), Color.GREEN.value)
                print("Placed at: x={} y={} ({})".format(x, y, placed))
            elif right_pressed:
                coords = x // cell_size, y // cell_size
                for row in range(coords[1] - wall_radius, coords[1] + wall_radius + 1):
                    for column in range(coords[0] - wall_radius, coords[0] + wall_radius + 1):
                        if (column - coords[0]) ** 2 + (row - coords[1]) ** 2 <= wall_radius ** 2:
                            if row < 0 or column < 0 or row >= max_row or column >= max_col or playground[row][
                                column].fill != Fill.FREE:
                                continue
                            pygame.gfxdraw.box(screen, (column * cell_size, row * cell_size, cell_size, cell_size),
                                               Color.YELLOW.value)
                            playground[row][column].fill = Fill.WALL
                print("Wall at: x={} y={}".format(x, y))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print(placed["start"])
                    if not placed["start"]:
                        continue
                    started = True
                    heapq.heappush(q, (0, (placed["start"],), playground[placed["start"][1]][placed["start"][0]]))
                elif event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT, dict()))
            elif event.type == pygame.VIDEORESIZE:
                size, width, height = event.size, event.w, event.h
                grid_init()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    wall_radius += 1
                    update_info()
                elif event.button == 4:
                    wall_radius -= 1
                    update_info()
    else:
        update_c = 0
        while len(q) > 0:
            distance, path, cell = heapq.heappop(q)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT, dict()))
                    continue
            cell.distance = distance
            if DEBUG:
                label = font_renderer.render(str(distance), 1, Color.ORANGE.value)
                screen.blit(label, (cell.x * cell_size + 1, cell.y * cell_size + 1))

                # will break with target near a wall, fix with proper cell class instead of constants
            for neighbor in [(cell.x - 1, cell.y), (cell.x + 1, cell.y), (cell.x, cell.y - 1),
                             (cell.x, cell.y + 1)]:
                if neighbor[1] < 0 or neighbor[0] < 0 or neighbor[1] >= max_row or neighbor[0] >= max_col:
                    continue
                if playground[neighbor[1]][neighbor[0]].fill == Fill.TARGET:
                    finish(path)
                    idle()
                elif playground[neighbor[1]][neighbor[0]].fill == Fill.FREE and not playground[neighbor[1]][
                    neighbor[0]].pushed:
                    heapq.heappush(q, (distance + 1, path + (neighbor,), playground[neighbor[1]][neighbor[0]]))
                    playground[neighbor[1]][neighbor[0]].pushed = True
                    if neighbor[1] - cell.y == 0:
                        # same row
                        if neighbor[1] - 1 >= 0:
                            playground[neighbor[1] - 1][neighbor[0]].reachable += 1
                        if neighbor[1] + 1 < max_row:
                            playground[neighbor[1] + 1][neighbor[0]].reachable += 1
                    else:
                        # same column
                        if neighbor[0] - 1 >= 0:
                            playground[neighbor[1]][neighbor[0] - 1].reachable += 1
                        if neighbor[0] + 1 < max_col:
                            playground[neighbor[1]][neighbor[0] + 1].reachable += 1
            for neighbor in [(cell.x - 1, cell.y - 1), (cell.x - 1, cell.y + 1), (cell.x + 1, cell.y - 1),
                             (cell.x + 1, cell.y + 1)]:
                if neighbor[1] < 0 or neighbor[0] < 0 or neighbor[1] >= max_row or neighbor[0] >= max_col:
                    continue
                if playground[neighbor[1]][neighbor[0]].reachable == 2 and not playground[neighbor[1]][
                    neighbor[0]].pushed:
                    heapq.heappush(q, (distance + 1, path + (neighbor,), playground[neighbor[1]][neighbor[0]]))
                    playground[neighbor[1]][neighbor[0]].pushed = True
                playground[neighbor[1]][neighbor[0]].reachable = 0
            update_c += 1
            if should_update and update_counter == update_c:
                clock.tick(MAX_TPS)
                pygame.display.update()
                update_c = 0
        idle()
    pygame.display.update()
    clock.tick(MAX_TPS)
