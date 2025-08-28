import pygame
import random

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Square")

# Цвета
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Параметры игры
square_y = HEIGHT // 2
square_size = 20
jump_speed = -10  # Скорость прыжка
gravity = 0.5  # Гравитация
velocity_y = 0
pipes = []
clouds = []
pipe_width = 50
pipe_gap = 150
pipe_speed = 3
score = 0
game_over = False
FPS = 60
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
last_gap_level = None
last_pipe_time = pygame.time.get_ticks()
last_cloud_time = pygame.time.get_ticks()
background_offset = 0  # Для сдвига фона при отскоке

def create_pipe():
    global last_gap_level
    levels = {1: 150, 2: 225, 3: 300, 4: 375, 5: 450}
    if last_gap_level is None:
        level = random.randint(1, 5)
    else:
        if last_gap_level == 1:
            possible = [3, 4, 5]
        elif last_gap_level == 2:
            possible = [4, 5]
        elif last_gap_level == 3:
            possible = [1, 5]
        elif last_gap_level == 4:
            possible = [1, 2]
        elif last_gap_level == 5:
            possible = [1, 2, 3]
        level = random.choice(possible)
    gap_y = levels[level]
    last_gap_level = level
    return {'x': WIDTH, 'top': gap_y - pipe_gap // 2, 'bottom': gap_y + pipe_gap // 2, 'passed': False}

def create_cloud():
    y = random.randint(50, HEIGHT // 3)
    size = random.randint(30, 70)
    x = WIDTH + random.randint(0, 200)
    return {'x': x, 'y': y, 'size': size}

# Инициализация первых труб и облаков
pipes.append(create_pipe())
for _ in range(3):
    cloud = create_cloud()
    cloud['x'] = random.randint(0, WIDTH)
    clouds.append(cloud)

def draw_cloud(cloud):
    x = (cloud['x'] + background_offset) % (WIDTH + cloud['size'] * 1.5)
    y, s = cloud['y'], cloud['size']
    pygame.draw.ellipse(screen, WHITE, (x, y, s * 1.5, s))
    pygame.draw.ellipse(screen, WHITE, (x + s * 0.3, y - s * 0.2, s * 0.8, s * 0.8))
    pygame.draw.ellipse(screen, WHITE, (x + s, y + s * 0.1, s * 0.7, s * 0.7))

def draw():
    screen.fill(SKY_BLUE)
    for cloud in clouds:
        draw_cloud(cloud)
    pygame.draw.rect(screen, YELLOW, (100, square_y, square_size, square_size))
    for pipe in pipes:
        pygame.draw.rect(screen, GREEN, (pipe['x'], 0, pipe_width, pipe['top']))
        pygame.draw.rect(screen, GREEN, (pipe['x'], pipe['bottom'], pipe_width, HEIGHT - pipe['bottom']))
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    if game_over:
        game_over_text = font.render("Game Over! Press R", True, (255, 0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))
    pygame.display.flip()

def update():
    global square_y, velocity_y, score, game_over, pipes, clouds, last_pipe_time, last_cloud_time, last_gap_level, background_offset
    if not game_over:
        velocity_y += gravity
        square_y += velocity_y
        if square_y >= HEIGHT - square_size:
            game_over = True
            square_y = HEIGHT - square_size
        if square_y < 0:
            square_y = 0
            velocity_y = 0
        for pipe in pipes:
            pipe['x'] -= pipe_speed
            if 100 < pipe['x'] + pipe_width and 100 + square_size > pipe['x']:
                if square_y < pipe['top'] or square_y + square_size > pipe['bottom']:
                    # Очень сильный отскок
                    velocity_y = -abs(velocity_y) * 2 if square_y < pipe['top'] else abs(velocity_y) * 2
                    square_y += -100 if square_y < pipe['top'] else 100
                    square_y = max(0, min(HEIGHT - square_size, square_y))
                    # Сдвинуть все трубы далеко вперед
                    for p in pipes:
                        p['x'] += 60
                    # Сдвинуть фон влево
                    background_offset -= 60
        pipes[:] = [pipe for pipe in pipes if pipe['x'] > -pipe_width]
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > 1500:
            pipes.append(create_pipe())
            last_pipe_time = current_time
        for pipe in pipes:
            if not pipe['passed'] and pipe['x'] + pipe_width < 100:
                score += 10
                pipe['passed'] = True
        # Облака
        for cloud in clouds:
            cloud['x'] -= pipe_speed / 2
        clouds[:] = [cloud for cloud in clouds if cloud['x'] + cloud['size'] * 1.5 > 0]
        if current_time - last_cloud_time > random.randint(1000, 3000):
            clouds.append(create_cloud())
            last_cloud_time = current_time
        # Постепенное возвращение фона
        if background_offset < 0:
            background_offset += pipe_speed / 2

def reset():
    global square_y, velocity_y, score, game_over, pipes, clouds, last_pipe_time, last_cloud_time, last_gap_level, background_offset
    square_y = HEIGHT // 2
    velocity_y = 0
    score = 0
    game_over = False
    last_gap_level = None
    pipes = [create_pipe()]
    clouds = []
    for _ in range(3):
        cloud = create_cloud()
        cloud['x'] = random.randint(0, WIDTH)
        clouds.append(cloud)
    last_pipe_time = pygame.time.get_ticks()
    last_cloud_time = pygame.time.get_ticks()
    background_offset = 0

# Основной цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                    velocity_y = jump_speed
            if event.key == pygame.K_r and game_over:
                reset()
    update()
    draw()
    clock.tick(FPS)

pygame.quit()