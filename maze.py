import pygame
import sys

# Screen size and cell size used by the maze window
# Width and height of SCREEN_SIZE should be divisible by CELL_SIZE
SCREEN_SIZE = (640, 480)
CELL_SIZE = 32

# Some useful numbers needed for the bit manipulation
# Left-most 4 bits store backtrack path, next 4 bits solution,
# next 4 bits border and last 4 bits walls knocked down.
# From left to right, each 4 bit cluster represents W, S, E, N
# NOTE: Border bits are not currently used
#                   directions
#                WSENWSENWSENWSEN
DEFAULT_CELL = 0b0000000000000000
#                |bt||s ||b ||w |
WALL_BITS = 0b0000000000001111
BACKTRACK_BITS = 0b1111000000000000
SOLUTION_BITS = 0b0000111100000000

# Indices match each other
# WALLS[i] corresponds with COMPASS[i], DIRECTION[i], and OPPOSITE_WALLS[i]
WALLS = [0b1000, 0b0100, 0b0010, 0b0001]
OPPOSITE_WALLS = [0b0010, 0b0001, 0b1000, 0b0100]
COMPASS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
DIRECTION = ['W', 'S', 'E', 'N']

# Colors
BLACK = (0, 0, 0, 255)
NO_COLOR = (0, 0, 0, 0)
WHITE = (255, 255, 255, 255)
GREEN = (0, 255, 0, 255)
RED = (255, 0, 0, 255)
BLUE = (0, 0, 255, 255)
LIGHT_BLUE = (0, 0, 255, 100)
PURPLE = (150, 0, 150, 255)


class Maze:
    def __init__(self, initial_state='idle'):
        # Maze set up
        self.state = initial_state
        self.w_cells = int(SCREEN_SIZE[0] / CELL_SIZE)
        self.h_cells = int(SCREEN_SIZE[1] / CELL_SIZE)
        self.total_cells = self.w_cells * self.h_cells
        self.maze_array = [DEFAULT_CELL] * self.total_cells

        # Pygame set up
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.background = pygame.Surface(self.screen.get_size())
        self.m_layer = pygame.Surface(self.screen.get_size())
        self.s_layer = pygame.Surface(self.screen.get_size())
        self.setup_maze_window()

    # Return cell neighbors within bounds of the maze
    # Use self.state to determine which neighbors should be included
    def cell_neighbors(self, cell):
        #  Logic for getting neighbors based on self.state
        x, y = self.x_y(cell)
        neighbors = []
        for i in range(4):
            new_x = x + COMPASS[i][0]
            new_y = y + COMPASS[i][1]
            if self.cell_in_bounds(new_x, new_y):
                new_cell = self.cell_index(new_x, new_y)
                if self.state == 'create':
                    if not (self.maze_array[new_cell] & WALL_BITS):
                        neighbors.append((new_cell, i))
                elif self.state == 'solve':
                    if (self.maze_array[cell] & WALLS[i]):
                        if not (self.maze_array[new_cell] & (BACKTRACK_BITS | SOLUTION_BITS)):
                            neighbors.append((new_cell, i))
        return neighbors

    # Connect two cells by knocking down the wall between them
    # Update wall bits of from_cell and to_cell
    def connect_cells(self, from_cell, to_cell, compass_index):
        self.maze_array[from_cell] |= WALLS[compass_index]
        self.maze_array[to_cell] |= OPPOSITE_WALLS[compass_index]
        self.draw_connect_cells(from_cell, compass_index)

    # Visit a cell along a possible solution path
    # Update solution bits of from_cell and backtrack bits of to_cell
    def visit_cell(self, from_cell, to_cell, compass_index):
        self.maze_array[from_cell] &= ~SOLUTION_BITS
        self.maze_array[from_cell] |= (WALLS[compass_index] << 8)
        self.maze_array[to_cell] |= (OPPOSITE_WALLS[compass_index] << 12)
        self.draw_visited_cell(from_cell)

    # Backtrack from cell
    # Blank out the solution bits so it is no longer on the solution path
    def backtrack(self, cell):
        self.maze_array[cell] &= ~SOLUTION_BITS
        self.draw_backtracked_cell(cell)

    # Visit cell in BFS search
    # Update backtrack bits for use in reconstruct_solution
    def bfs_visit_cell(self, cell, from_compass_index):
        self.maze_array[cell] |= (OPPOSITE_WALLS[from_compass_index] << 12)
        self.draw_bfs_visited_cell(cell)

    # Reconstruct path to start using backtrack bits
    def reconstruct_solution(self, cell):
        self.draw_visited_cell(cell)
        prev_cell_bits = (self.maze_array[cell] & BACKTRACK_BITS) >> 12
        try:
            i = WALLS.index(prev_cell_bits)
        except ValueError:
            print('ERROR - BACKTRACK BITS INVALID!')
        x, y = self.x_y(cell)
        prev_x = x + COMPASS[i][0]
        prev_y = y + COMPASS[i][1]
        prev_cell = self.cell_index(prev_x, prev_y)
        self.maze_array[prev_cell] |= (OPPOSITE_WALLS[i] << 8)
        self.refresh_maze_view()
        if prev_cell != 0:
            self.reconstruct_solution(prev_cell)

    # Check if x, y values of cell are within bounds of maze
    def cell_in_bounds(self, x, y):
        return ((x >= 0) and (y >= 0) and (x < self.w_cells)
                and (y < self.h_cells))

    # Cell index from x, y values
    def cell_index(self, x, y):
        return y * self.w_cells + x

    # x, y values from a cell index
    def x_y(self, index):
        x = index % self.w_cells
        y = int(index / self.w_cells)
        return x, y

    # x, y point values from a cell index
    def x_y_pos(self, index):
        x, y = self.x_y(index)
        x_pos = x * CELL_SIZE
        y_pos = y * CELL_SIZE
        return x_pos, y_pos

    # Build solution array using solution bits
    # Use DIRECTION to return cardinal directions representing solution path
    def solution_array(self):
        solution = []

        # TODO: Logic to return cardinal directions representing solution path

        return solution

    # 'Knock down' wall between two cells, use in creation as walls removed
    def draw_connect_cells(self, from_cell, compass_index):
        x_pos, y_pos = self.x_y_pos(from_cell)
        if compass_index == 0:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos, y_pos + 1),
                             (x_pos, y_pos + CELL_SIZE - 1))
        elif compass_index == 1:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos + 1,
                             y_pos + CELL_SIZE), (x_pos + CELL_SIZE - 1,
                             y_pos + CELL_SIZE))
        elif compass_index == 2:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos + CELL_SIZE,
                             y_pos + 1), (x_pos + CELL_SIZE,
                             y_pos + CELL_SIZE - 1))
        elif compass_index == 3:
            pygame.draw.line(self.m_layer, NO_COLOR, (x_pos + 1, y_pos),
                             (x_pos + CELL_SIZE - 1, y_pos))

    # Draw green square at cell, use to visualize solution path being explored
    def draw_visited_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, GREEN, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))

    # Draws a red square at cell, use to change cell to visualize backtrack
    def draw_backtracked_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, RED, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))

    # Draw green square at cell, use to visualize solution path being explored
    def draw_bfs_visited_cell(self, cell):
        x_pos, y_pos = self.x_y_pos(cell)
        pygame.draw.rect(self.s_layer, LIGHT_BLUE, pygame.Rect(x_pos, y_pos,
                         CELL_SIZE, CELL_SIZE))

    # Process events, add each layer to screen (blip) and refresh (flip)
    # Call this at the end of each traversal step to watch the maze as it is
    # generated. Skip call until end of creation/solution to make faster.
    def refresh_maze_view(self):
        check_for_exit()
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.s_layer, (0, 0))
        self.screen.blit(self.m_layer, (0, 0))
        pygame.display.flip()

    def setup_maze_window(self):
        # Set up window and layers
        pygame.display.set_caption('Maze Generation and Solving')
        pygame.mouse.set_visible(0)
        self.background = self.background.convert()
        self.background.fill(WHITE)
        self.m_layer = self.m_layer.convert_alpha()
        self.m_layer.fill(NO_COLOR)
        self.s_layer = self.s_layer.convert_alpha()
        self.s_layer.fill(NO_COLOR)

        # Draw grid lines (will be whited out as walls knocked down)
        for y in range(self.h_cells + 1):
            pygame.draw.line(self.m_layer, BLACK, (0, y * CELL_SIZE),
                             (SCREEN_SIZE[0], y * CELL_SIZE))
        for x in range(self.w_cells + 1):
            pygame.draw.line(self.m_layer, BLACK, (x * CELL_SIZE, 0),
                             (x * CELL_SIZE, SCREEN_SIZE[1]))

        # Color start cell blue and exit cell purple.
        # Assumes start at top-left and exit at bottom-right
        pygame.draw.rect(self.s_layer, BLUE,
                         pygame.Rect(0, 0, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(self.s_layer, PURPLE, pygame.Rect(
                         SCREEN_SIZE[0] - CELL_SIZE, SCREEN_SIZE[1] -
                         CELL_SIZE, CELL_SIZE, CELL_SIZE))


def check_for_exit():
    # Aims for 60fps, checks for events.
    # Without event check every frame, window will not exit!
    clock = pygame.time.Clock()
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit(0)
