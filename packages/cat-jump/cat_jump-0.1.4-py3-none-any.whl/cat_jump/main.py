import os
import sys
import termios
import tty
import fcntl
import time
import random
from wcwidth import wcwidth

cat_frames = {
    "idle": [" /\\_/\\", "ฅ •ﻌ• ฅ"],
    "jump": [" /\\_/\\", "ฅ >ﻌ< ฅ"],
    "fall": [" /\\_/\\", "ฅ >ﻌ< ฅ"],
    "dead": [" /\\_/\\", "ฅ xﻌx ฅ"]
}

CAT_HEIGHT = 2
CAT_WIDTH = len(cat_frames["idle"][0])
SCREEN_WIDTH = 50
SCREEN_HEIGHT = 10
CAT_POS_X = 5
GROUND_Y = SCREEN_HEIGHT - CAT_HEIGHT

GRAVITY = 0.05
JUMP_POWER = -0.9
OBSTACLE_MIN_GAP = 35
MAX_OBSTACLES = 5
BACKGROUND_CHARS = ['*', '.', "'", '"', '~', '-', '+']
GROUND_OBSTACLE_EMOJIS = ['🧸', '💣', '🚧', '🩵', '🔧', '🔥', '📦', '🧱', '🪨']

CAT_UPDATE_INTERVAL = 0.016
FRAME_FIXED_DELAY = 0.02

def setup_keyboard():
    fd = sys.stdin.fileno()
    old_term = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    old_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)
    return fd, old_term, old_flags

def restore_keyboard(fd, old_term, old_flags):
    termios.tcsetattr(fd, termios.TCSADRAIN, old_term)
    fcntl.fcntl(fd, fcntl.F_SETFL, old_flags)

def draw_screen(cat_state, cat_y, obstacles, frame, background_objects):
    print("\033[H", end="")
    screen_lines = [" " * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]

    for bg in background_objects:
        y, x, char = bg['y'], int(bg['x']), bg['char']
        if 0 <= y < SCREEN_HEIGHT and 0 <= x < SCREEN_WIDTH:
            screen_lines[y] = screen_lines[y][:x] + char + screen_lines[y][x+1:]

    cat_frame = cat_frames[cat_state]
    for i in range(CAT_HEIGHT):
        y = cat_y + i
        if 0 <= y < SCREEN_HEIGHT:
            line = list(screen_lines[y])
            for j, c in enumerate(cat_frame[i]):
                if CAT_POS_X + j < SCREEN_WIDTH:
                    line[CAT_POS_X + j] = c
            screen_lines[y] = "".join(line)

    for obs in obstacles:
        for dy in range(obs['height']):
            y = obs['y'] - dy
            if 0 <= y < SCREEN_HEIGHT:
                line = list(screen_lines[y])
                for dx in range(obs['width']):
                    x = int(obs['x']) + dx
                    if 0 <= x < SCREEN_WIDTH:
                        emoji = obs['emoji']
                        line[x] = emoji
                        if len(emoji) == 1 and wcwidth(emoji) == 2 and x + 1 < SCREEN_WIDTH:
                            line[x + 1] = " "
                screen_lines[y] = "".join(line)

    try:
        sys.stdout.write(f"Score: {frame}\n")
        sys.stdout.write("\n".join(screen_lines) + "\n")
        sys.stdout.write("-" * SCREEN_WIDTH + "\n")
        sys.stdout.flush()
    except BlockingIOError:
        pass

def run():
    frame = 0
    last_beep_score = -100
    position_y = float(GROUND_Y)
    velocity_y = 0
    is_jumping = False
    obstacles = []
    background_objects = []
    cat_state = "idle"

    os.system('clear')
    print("\n" * (SCREEN_HEIGHT + 2))
    fd, old_term, old_flags = setup_keyboard()

    last_cat_update_time = time.time()
    last_frame_time = time.time()

    try:
        while True:
            now = time.time()

            key = ''
            try:
                key = sys.stdin.read(3)
            except IOError:
                pass

            if (key == " " or key == "\x1b[A") and not is_jumping:
                velocity_y = JUMP_POWER
                is_jumping = True

            if now - last_cat_update_time >= CAT_UPDATE_INTERVAL:
                position_y += velocity_y
                velocity_y += GRAVITY
                if position_y >= GROUND_Y:
                    position_y = GROUND_Y
                    velocity_y = 0
                    is_jumping = False
                cat_state = "jump" if velocity_y < 0 else "fall" if is_jumping else "idle"
                last_cat_update_time = now

            if now - last_frame_time >= FRAME_FIXED_DELAY:
                obstacle_speed = 0.4 + min(frame / 2000, 1.5)

                for obs in obstacles:
                    obs['x'] -= obstacle_speed
                obstacles = [obs for obs in obstacles if obs['x'] + obs['width'] > 0]

                for bg in background_objects:
                    bg['x'] -= 1
                background_objects = [bg for bg in background_objects if bg['x'] > 0]

                if random.random() < 0.05:
                    char = random.choice(BACKGROUND_CHARS)
                    y = random.randint(1, SCREEN_HEIGHT - CAT_HEIGHT - 3)
                    background_objects.append({'x': float(SCREEN_WIDTH - 1), 'y': y, 'char': char})

                if len(obstacles) < MAX_OBSTACLES and (not obstacles or obstacles[-1]['x'] < SCREEN_WIDTH - OBSTACLE_MIN_GAP):
                    if random.random() < 0.1:
                        while True:
                            height = random.choice([1, 2])
                            width = random.choice([1, 2])
                            if height == 2 and width == 2:
                                continue
                            break
                        emoji = random.choice(GROUND_OBSTACLE_EMOJIS)
                        obstacles.append({
                            'x': float(SCREEN_WIDTH - 1),
                            'y': SCREEN_HEIGHT - 1,
                            'height': height,
                            'width': width,
                            'emoji': emoji
                        })

                cat_y = int(position_y)
                for obs in obstacles:
                    for dy in range(obs['height']):
                        obs_y = obs['y'] - dy
                        for dx in range(obs['width']):
                            x = int(obs['x']) + dx
                            if x in range(CAT_POS_X, CAT_POS_X + CAT_WIDTH) and obs_y in range(cat_y, cat_y + CAT_HEIGHT):
                                cat_state = "dead"
                                draw_screen(cat_state, cat_y, obstacles, frame, background_objects)
                                print("Game Over! meow!")
                                return

                draw_screen(cat_state, int(position_y), obstacles, frame, background_objects)
                frame += 1

                if frame % 100 == 0 and frame != last_beep_score:
                    print('\a', end='')
                    last_beep_score = frame

                last_frame_time = now

    except KeyboardInterrupt:
        print("\nGame terminated! meow!")
    finally:
        restore_keyboard(fd, old_term, old_flags)

def main():
    while True:
        run()
        answer = input("Play again? (y/n): ").strip().lower()
        if answer != 'y':
            print("nyan... Goodbye")
            break
        os.system('clear')

if __name__ == "__main__":
    main()