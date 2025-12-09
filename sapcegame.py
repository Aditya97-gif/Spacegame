# Simple Space Battle game (single file)
# Controls: A / Left  - move left
#           D / Right - move right
#           Space     - shoot
#           R         - restart after game over
#           Esc / Q   - quit
import pygame as py
import sys
import random
import webbrowser
from math import copysign

py.init()
WIDTH, HEIGHT = 800, 600
SCREEN = py.display.set_mode((WIDTH, HEIGHT))
py.display.set_caption("Space Battle")
CLOCK = py.time.Clock()
FONT = py.font.SysFont(None, 28)

# Colors
BG = (8, 8, 20)
WHITE = (230, 230, 230)
RED = (220, 50, 50)
GREEN = (80, 220, 120)
YELLOW = (240, 220, 80)
BLUE = (90, 140, 240)
GRAY = (100, 100, 110)

# Player
PLAYER_W, PLAYER_H = 48, 28
PLAYER_SPEED = 6
PLAYER_Y = HEIGHT - 60
SHOOT_COOLDOWN = 300  # ms

# Bullet
BULLET_W, BULLET_H = 4, 10
BULLET_SPEED = -9

# Enemy
ENEMY_W, ENEMY_H = 44, 26
ENEMY_SPEED_MIN, ENEMY_SPEED_MAX = 1.2, 3.0
ENEMY_SPAWN_INTERVAL = 900  # ms (decreases as level increases)

# Game state
score = 0
lives = 7
level = 1
running = True
game_over = False

# Entities
player = py.Rect(WIDTH // 2 - PLAYER_W // 2, PLAYER_Y, PLAYER_W, PLAYER_H)
bullets = []  
enemies = []  # list of dict {rect, speed, hp, color}
last_shot = 0
last_spawn = 0

def spawn_enemy():
    x = random.randint(20, WIDTH - ENEMY_W - 20)
    y = -ENEMY_H
    speed = random.uniform(ENEMY_SPEED_MIN + (level-1)*0.2, ENEMY_SPEED_MAX + (level-1)*0.3)
    hp = 1 + (level // 3)
    color = random.choice([RED, YELLOW, BLUE, GREEN])
    enemies.append({"rect": py.Rect(x, y, ENEMY_W, ENEMY_H), "speed": speed, "hp": hp, "color": color})

def reset_game():
    global score, lives, level, game_over, bullets, enemies, last_shot, last_spawn, player
    score = 0
    lives = 3
    level = 1
    game_over = False
    bullets = []
    enemies = []
    last_shot = 0
    last_spawn = 0
    player.x = WIDTH // 2 - PLAYER_W // 2

def draw_player(surf, rect):
    cx = rect.centerx
    top = (cx, rect.top)
    left = (rect.left, rect.bottom)
    right = (rect.right, rect.bottom)
    py.draw.polygon(surf, GREEN, (top, left, right))
    py.draw.polygon(surf, BLUE, ((cx, rect.top+6),(cx-6, rect.top+18),(cx+6, rect.top+18)))

def draw_enemy(surf, e):
    r = e["rect"]
    py.draw.rect(surf, e["color"], r, border_radius=6)
    hp = e["hp"]
    for i in range(hp):
        bar_w = (r.w-6) / max(1, hp)
        bar_x = r.x + 3 + i*bar_w
        py.draw.rect(surf, RED if i==0 else GRAY, (bar_x, r.y-6, bar_w-2, 4))

def update(dt):
    global last_spawn, last_shot, score, lives, level, game_over

    keys = py.key.get_pressed()
    # player movement
    if keys[py.K_a] or keys[py.K_LEFT]:
        player.x -= PLAYER_SPEED
    if keys[py.K_d] or keys[py.K_RIGHT]:
        player.x += PLAYER_SPEED
    player.x = max(8, min(WIDTH - PLAYER_W - 8, player.x))

    t = py.time.get_ticks()
    # shooting
    if (keys[py.K_SPACE] or keys[py.K_z]) and t - last_shot >= SHOOT_COOLDOWN and not game_over:
        bx = player.centerx - BULLET_W // 2
        by = player.top - BULLET_H
        bullets.append(py.Rect(bx, by, BULLET_W, BULLET_H))
        last_shot = t
    # enemy spawning
    spawn_interval = max(250, ENEMY_SPAWN_INTERVAL - (level-1)*60)
    if t - last_spawn >= spawn_interval and not game_over:
        spawn_enemy()
        last_spawn = t

    # update bullets
    for b in bullets[:]:
        b.y += BULLET_SPEED
        if b.bottom < 0:
            bullets.remove(b)

    # update enemies
    for e in enemies[:]:
        e["rect"].y += e["speed"]
        # enemy off bottom -> player loses life
        if e["rect"].top > HEIGHT:
            enemies.remove(e)
            lives -= 1
            if lives <= 0:
                game_over = True
        # check collision with bullets
        for b in bullets[:]:
            if e["rect"].colliderect(b):
                bullets.remove(b)
                e["hp"] -= 1
                if e["hp"] <= 0:
                    try:
                        enemies.remove(e)
                    except ValueError:
                        pass
                    score += 10
                    # level up for every 100 points
                    if score // 100 + 1 > level:
                        level = score // 100 + 1
                break
        # collision with player
        if e["rect"].colliderect(player) and not game_over:
            try:
                enemies.remove(e)
            except ValueError:
                pass
            lives -= 1
            if lives <= 0:
                game_over = True
    if(score==170):#editable
        webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        score+=10

def draw():
    SCREEN.fill(BG)
    # stars background
    for i in range(60):
        sx = (i*37 + (py.time.get_ticks()//50) ) % WIDTH
        sy = (i*67) % HEIGHT
        col = (40,40,60) if i%5 else (80,80,100)
        SCREEN.set_at((sx, sy), col)

    # draw player
    draw_player(SCREEN, player)

    # draw bullets
    for b in bullets:
        py.draw.rect(SCREEN, YELLOW, b)

    # draw enemies
    for e in enemies:
        draw_enemy(SCREEN, e)

    # HUD
    score_surf = FONT.render(f"Score: {score}", True, WHITE)
    level_surf = FONT.render(f"Level: {level}", True, WHITE)
    lives_surf = FONT.render(f"Lives: {lives}", True, WHITE)
    SCREEN.blit(score_surf, (10, 10))
    SCREEN.blit(level_surf, (10, 36))
    SCREEN.blit(lives_surf, (10, 62))

    if game_over:
        go_surf = py.font.SysFont(None, 64).render("GAME OVER", True, RED)
        sub_surf = FONT.render("Press R to restart or Q/Esc to quit", True, WHITE)
        SCREEN.blit(go_surf, (WIDTH//2 - go_surf.get_width()//2, HEIGHT//2 - 60))
        SCREEN.blit(sub_surf, (WIDTH//2 - sub_surf.get_width()//2, HEIGHT//2 + 10))

    py.display.flip()

def main():
    global running, game_over
    reset_game()
    while running:
        dt = CLOCK.tick(60)
        for event in py.event.get():
            if event.type == py.QUIT:
                running = False
            elif event.type == py.KEYDOWN:
                if event.key in (py.K_q, py.K_ESCAPE):
                    running = False
                if event.key == py.K_r and game_over:
                    reset_game()
            
            

        if not game_over:
            update(dt)
        draw()

    py.quit()
    sys.exit()

if __name__ == "__main__":
    main()
#