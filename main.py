import pygame, sys

pygame.init()
W, H = 800, 480
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Frame-by-Frame Animator")

# --- State ---
frames = [pygame.Surface((W, H), pygame.SRCALPHA)]
current_frame = 0
drawing = False
erasing = False
playback = False
play_index = 0
brush_color = (255, 255, 255)
brush_size = 4

def new_frame():
    global frames, current_frame
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    frames.insert(current_frame+1, surf)
    current_frame += 1

def draw_ui():
    font = pygame.font.SysFont("consolas", 18)
    txt = f"Frame {current_frame+1}/{len(frames)} | N: New Frame | ←/→: Switch | Space: Play | R: Reset"
    label = font.render(txt, True, (200,200,200))
    screen.blit(label, (10, H-25))

running = True
while running:
    dt = clock.tick(30)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1: drawing = True
            if e.button == 3: erasing = True
        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1: drawing = False
            if e.button == 3: erasing = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_n: new_frame()
            if e.key == pygame.K_LEFT: current_frame = max(0, current_frame-1)
            if e.key == pygame.K_RIGHT: current_frame = min(len(frames)-1, current_frame+1)
            if e.key == pygame.K_SPACE: playback = not playback; play_index = 0
            if e.key == pygame.K_r: frames = [pygame.Surface((W,H), pygame.SRCALPHA)]; current_frame=0; playback=False

    if drawing:
        pygame.draw.circle(frames[current_frame], brush_color, pygame.mouse.get_pos(), brush_size)
    if erasing:
        pygame.draw.circle(frames[current_frame], (0,0,0,0), pygame.mouse.get_pos(), brush_size)

    screen.fill((20,20,30))

    if playback:
        screen.blit(frames[play_index], (0,0))
        play_index += 1
        if play_index >= len(frames): play_index = 0
    else:
        # Onion skin: show previous frame faintly
        if current_frame > 0:
            prev = frames[current_frame-1].copy()
            prev.set_alpha(80)
            screen.blit(prev, (0,0))
        screen.blit(frames[current_frame], (0,0))

    draw_ui()
    pygame.display.flip()
