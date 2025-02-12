import pygame
import os
import heapq
import random

pygame.init()

screen_width = 800
screen_height = 600
grid_size = 20
cell_size = screen_width // grid_size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("CHASE")

background_image = pygame.image.load(os.path.join("background.jpg")).convert()
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
background2_image = pygame.image.load(os.path.join("background2.png")).convert_alpha()
background2_image = pygame.transform.scale(background2_image, (screen_width, screen_height))
tree_image = pygame.image.load(os.path.join("tree.png")).convert_alpha()
tree_size = (cell_size, cell_size)
tree_image = pygame.transform.scale(tree_image, tree_size)
player_image = pygame.image.load(os.path.join("char.png")).convert_alpha()
player_size = (cell_size, cell_size)
player_image = pygame.transform.scale(player_image, player_size)
enemy_image = pygame.image.load(os.path.join("enemy.png")).convert_alpha()
enemy_size = (cell_size, cell_size)
enemy_image = pygame.transform.scale(enemy_image, enemy_size)
play_button_image = pygame.image.load(os.path.join("play.png")).convert_alpha()
play_button_image = pygame.transform.scale(play_button_image, (64, 64))
blood_image = pygame.image.load(os.path.join("blood.png")).convert_alpha()
pickup_image = pygame.image.load(os.path.join("pickup.png")).convert_alpha()
pickup_size = (cell_size, cell_size)
pickup_image = pygame.transform.scale(pickup_image, pickup_size)

font = pygame.font.SysFont(None, 37)
fiendish_font = pygame.font.Font("fiendish.ttf", 64)
small_font = pygame.font.SysFont(None, 16)

pygame.mixer.music.load("bg.mp3")
pygame.mixer.music.set_volume(0.25)
step_sound = pygame.mixer.Sound("step.mp3")
step_sound.set_volume(0.25)
game_over_sound = pygame.mixer.Sound("gameover.mp3")

pickup_sound = pygame.mixer.Sound("pickup.mp3")

maze_pattern = [
    "####################",
    "#          #       #",
    "###  ##### # ##### #",
    "# #  #           # #",
    "# #  #   # ##### # #",
    "#      #       #   #",
    "#    ##### # ### # #",
    "#          #   # # #",
    "####  ############ #",
    "#            #     #",
    "#   ######## # #####",
    "#          # #     #",
    "##   ##### # # ### #",
    "#          #       #",
    "####################"
]

def is_inside_rect(point, rect):
    x, y = point
    rx, ry, rw, rh = rect
    return rx < x < rx + rw and ry < y < ry + rh

def is_inside_maze(x, y):
    return 0 <= x < len(maze_pattern[0]) and 0 <= y < len(maze_pattern)

def heuristic(start, goal):
    return abs(goal[0] - start[0]) + abs(goal[1] - start[1])

def astar(start, goal):
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    open_list = [(heuristic(start, goal), start)]
    heapq.heapify(open_list)
    closed_list = set()
    parent = {}
    cost = {start: 0}
    while open_list:
        current_cost, current_node = heapq.heappop(open_list)
        if current_node == goal:
            path = []
            while current_node in parent:
                path.append(current_node)
                current_node = parent[current_node]
            path.append(start)
            path.reverse()
            return path
        closed_list.add(current_node)
        for dx, dy in directions:
            neighbor = (current_node[0] + dx, current_node[1] + dy)
            if is_inside_maze(*neighbor) and maze_pattern[neighbor[1]][neighbor[0]] != '#':
                new_cost = cost[current_node] + 1
                if neighbor not in closed_list or new_cost < cost.get(neighbor, float('inf')):
                    cost[neighbor] = new_cost
                    parent[neighbor] = current_node
                    heapq.heappush(open_list, (new_cost + heuristic(neighbor, goal), neighbor))
    return []

def generate_pickup_position():
    while True:
        x = random.randint(0, grid_size - 1)
        y = random.randint(0, grid_size - 1)
        if is_inside_maze(x, y) and maze_pattern[y][x] != '#':
            return x, y

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

play_button_clicked = False

player_x = 2
player_y = 1

enemies = [(grid_size - 1, 1)]  # Store enemy positions as tuples (x, y)
pickup_x, pickup_y = generate_pickup_position()
score = 0
enemy_spawn_countdown = 10

enemy_timer = pygame.time.get_ticks()
enemy_interval = 333

pygame.mixer.music.play(-1)

running = True
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if is_inside_rect(mouse_pos,
                              (screen_width // 2 - play_button_image.get_width() // 2,
                               screen_height // 2 - play_button_image.get_height() // 2,
                               play_button_image.get_width(), play_button_image.get_height())):
                play_button_clicked = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if player_y > 0 and maze_pattern[player_y - 1][player_x] != '#':
                    player_y -= 1
                    step_sound.play()
            elif event.key == pygame.K_s:
                if player_y < len(maze_pattern) - 1 and maze_pattern[player_y + 1][player_x] != '#':
                    player_y += 1
                    step_sound.play()
            elif event.key == pygame.K_a:
                if player_x > 0 and maze_pattern[player_y][player_x - 1] != '#':
                    player_x -= 1
                    step_sound.play()
            elif event.key == pygame.K_d:
                if player_x < len(maze_pattern[0]) - 1 and maze_pattern[player_y][player_x + 1] != '#':
                    player_x += 1
                    step_sound.play()

    if current_time - enemy_timer > enemy_interval:
        for enemy_index, enemy_pos in enumerate(enemies):
            path = astar(enemy_pos, (player_x, player_y))
            if len(path) > 1:
                enemies[enemy_index] = path[1]
        enemy_timer = current_time

    for enemy_pos in enemies:
        if player_x == enemy_pos[0] and player_y == enemy_pos[1]:
            print("Game Over")
            game_over_sound.play()
            pygame.mixer.music.stop()
            running = False

    if player_x == pickup_x and player_y == pickup_y:
        score += 1
        pickup_x, pickup_y = generate_pickup_position()
        pickup_sound.play()

    if not play_button_clicked:
        screen.blit(background_image, (0, 0))
        title_text = fiendish_font.render("MAZE GAME", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 3))
        screen.blit(title_text, title_rect)
        screen.blit(play_button_image, (screen_width // 2 - play_button_image.get_width() // 2,
                                        screen_height // 2 - play_button_image.get_height() // 2))
    else:
        darken_surface = pygame.Surface((screen_width, screen_height))
        darken_surface.set_alpha(200)
        darken_surface.fill((0, 0, 0))
        screen.blit(background2_image, (0, 0))
        screen.blit(darken_surface, (0, 0))

        for y, row in enumerate(maze_pattern):
            for x, char in enumerate(row):
                if char == '#':
                    screen.blit(tree_image, (x * cell_size, y * cell_size))
                    screen.blit(tree_image, (x * cell_size + tree_size[0] // 2, y * cell_size))

        screen.blit(player_image, (player_x * cell_size, player_y * cell_size))
        for enemy_pos in enemies:
            screen.blit(enemy_image, (enemy_pos[0] * cell_size, enemy_pos[1] * cell_size))
        screen.blit(pickup_image, (pickup_x * cell_size, pickup_y * cell_size))

        draw_text(screen, f"Score: {score}", font, (255, 255, 255), screen_width - 150, 10)

    pygame.display.update()

    if score >= enemy_spawn_countdown:
        enemy_spawn_countdown += 10
        enemies.append((grid_size - 1, 1))

game_over_surface = pygame.Surface((screen_width, screen_height))
game_over_surface.set_alpha(128)
game_over_surface.fill((0, 0, 0))
screen.blit(game_over_surface, (0, 0))
draw_text(screen, "GAME OVER", fiendish_font, (255, 255, 255), screen_width // 5, screen_height // 3)
pygame.display.update()

retry_button_clicked = False
while not retry_button_clicked:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            retry_button_clicked = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if is_inside_rect(mouse_pos, retry_button_rect):
                retry_button_clicked = True
                running = False
    pygame.display.update()

pygame.quit()
