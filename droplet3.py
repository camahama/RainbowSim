import pygame
import math
import sys

# --- Constants ---
# Logisk upplösning för simuleringen
WIDTH, HEIGHT = 1200, 800
BACKGROUND_COLOR = (5, 5, 5) 
DROP_CENTER = (WIDTH // 2, 200)
DROP_RADIUS = 23 

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BUTTON_COLOR = (50, 50, 80)
BUTTON_ACTIVE_COLOR = (80, 100, 80)
BUTTON_CLEAR_COLOR = (100, 50, 50) 
DROP_FILL_COLOR = (20, 20, 60)
DROP_OUTLINE_COLOR = (200, 200, 220)

RAINBOW_DATA = [
    {"name": "Red",    "rgb": (255, 0, 0),     "n": 1.331},
    {"name": "Orange", "rgb": (255, 127, 0),   "n": 1.333},
    {"name": "Yellow", "rgb": (255, 255, 0),   "n": 1.335},
    {"name": "Green",  "rgb": (0, 255, 0),     "n": 1.338},
    {"name": "Blue",   "rgb": (0, 0, 255),     "n": 1.343},
    {"name": "Indigo", "rgb": (75, 0, 130),    "n": 1.345},
    {"name": "Violet", "rgb": (148, 0, 211),   "n": 1.348},
]

def calculate_ray_path_from_bottom(x_offset, n_color, num_reflections):
    points = []
    start_x = DROP_CENTER[0] + x_offset
    start_y = HEIGHT
    points.append((start_x, start_y))
    if abs(x_offset) > DROP_RADIUS: return points 
    dy_entry = math.sqrt(DROP_RADIUS**2 - x_offset**2)
    entry_x = start_x
    entry_y = DROP_CENTER[1] + dy_entry
    points.append((entry_x, entry_y))
    try: alpha = math.asin(x_offset / DROP_RADIUS)
    except ValueError: return points
    sin_beta = (1.0003 / n_color) * math.sin(alpha)
    if abs(sin_beta) > 1: return points 
    beta = math.asin(sin_beta)
    theta_current = math.atan2(dy_entry, x_offset)
    rotation_step = -(math.pi - 2 * beta)
    for _ in range(num_reflections):
        theta_current += rotation_step
        ref_x = DROP_CENTER[0] + DROP_RADIUS * math.cos(theta_current)
        ref_y = DROP_CENTER[1] + DROP_RADIUS * math.sin(theta_current)
        points.append((ref_x, ref_y))
    theta_current += rotation_step
    exit_x = DROP_CENTER[0] + DROP_RADIUS * math.cos(theta_current)
    exit_y = DROP_CENTER[1] + DROP_RADIUS * math.sin(theta_current)
    points.append((exit_x, exit_y))
    final_ray_angle = theta_current - alpha
    end_x = exit_x + 3000 * math.cos(final_ray_angle) 
    end_y = exit_y + 3000 * math.sin(final_ray_angle)
    points.append((end_x, end_y))
    return points

def draw_buttons(surface, font, primary_visible, secondary_visible):
    buttons = []
    start_x = 20
    start_y = 20
    p_text = f"Primär: {'RENSA' if primary_visible else 'STARTA'}"
    surf = font.render(p_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    color = BUTTON_CLEAR_COLOR if primary_visible else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, GRAY, rect, 2, border_radius=5)
    surface.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "toggle_primary"})
    start_x += rect.width + 20
    s_text = f"Sekundär: {'RENSA' if secondary_visible else 'STARTA'}"
    surf = font.render(s_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    color = BUTTON_CLEAR_COLOR if secondary_visible else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, GRAY, rect, 2, border_radius=5)
    surface.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "toggle_secondary"})
    
    start_x += rect.width + 30
    back_text = "Meny"
    surf = font.render(back_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, 80, 35)
    pygame.draw.rect(surface, (150, 50, 50), rect, border_radius=5)
    surface.blit(surf, (rect.centerx - surf.get_width()//2, rect.centery - surf.get_height()//2))
    buttons.append({"rect": rect, "action": "back"})
    return buttons

def main(screen=None):
    if screen is None:
        pygame.init()
        screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Ljusspridning från en regndroppe")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    
    # Canvas för intern rendering (fast upplösning)
    canvas = pygame.Surface((WIDTH, HEIGHT))
    
    primary_canvas = pygame.Surface((WIDTH, HEIGHT))
    primary_canvas.fill((0, 0, 0))
    secondary_canvas = pygame.Surface((WIDTH, HEIGHT))
    secondary_canvas.fill((0, 0, 0))
    
    animating_primary = False
    primary_visible = False 
    p_current_offset = -DROP_RADIUS * 0.99 
    animating_secondary = False
    secondary_visible = False
    s_current_offset = -DROP_RADIUS * 0.99 
    step_size = 0.1 
    rays_to_draw_per_frame = 1 
    buttons = []

    running = True
    win_w, win_h = screen.get_width(), screen.get_height()

    while running:
        # Beräkna skala och offset för att behålla aspect ratio (Letterboxing)
        scale = min(win_w / WIDTH, win_h / HEIGHT)
        new_w = int(WIDTH * scale)
        new_h = int(HEIGHT * scale)
        offset_x = (win_w - new_w) // 2
        offset_y = (win_h - new_h) // 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                win_w, win_h = event.w, event.h
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    # Konvertera musposition till logiska koordinater
                    if offset_x <= mx < offset_x + new_w and offset_y <= my < offset_y + new_h:
                        logical_mx = (mx - offset_x) / scale
                        logical_my = (my - offset_y) / scale
                        logical_pos = (logical_mx, logical_my)
                        
                        for btn in buttons:
                            if btn["rect"].collidepoint(logical_pos):
                                if btn["action"] == "toggle_primary":
                                    if primary_visible:
                                        animating_primary = False; primary_visible = False; primary_canvas.fill((0,0,0))
                                    else:
                                        animating_primary = True; primary_visible = True; p_current_offset = -DROP_RADIUS * 0.99; primary_canvas.fill((0,0,0))
                                elif btn["action"] == "toggle_secondary":
                                    if secondary_visible:
                                        animating_secondary = False; secondary_visible = False; secondary_canvas.fill((0,0,0))
                                    else:
                                        animating_secondary = True; secondary_visible = True; s_current_offset = -DROP_RADIUS * 0.99; secondary_canvas.fill((0,0,0))
                                elif btn["action"] == "back":
                                    running = False

        if animating_primary:
            for _ in range(rays_to_draw_per_frame):
                if p_current_offset > DROP_RADIUS * 0.99: animating_primary = False; break
                offset = p_current_offset
                for data in RAINBOW_DATA:
                    col = (*data["rgb"], 50) 
                    path = calculate_ray_path_from_bottom(offset, data["n"], 1)
                    if len(path) >= 2:
                        temp = pygame.Surface((WIDTH, HEIGHT))
                        pygame.draw.lines(temp, col, False, path, 1)
                        primary_canvas.blit(temp, (0,0), special_flags=pygame.BLEND_ADD)
                p_current_offset += step_size

        if animating_secondary:
            for _ in range(rays_to_draw_per_frame):
                if s_current_offset > DROP_RADIUS * 0.99: animating_secondary = False; break
                offset = s_current_offset
                for data in RAINBOW_DATA:
                    col = (*data["rgb"], 0)
                    path = calculate_ray_path_from_bottom(offset, data["n"], 2)
                    if len(path) >= 2:
                        temp = pygame.Surface((WIDTH, HEIGHT))
                        pygame.draw.lines(temp, col, False, path, 1)
                        secondary_canvas.blit(temp, (0,0), special_flags=pygame.BLEND_ADD)
                s_current_offset += step_size

        canvas.fill(BACKGROUND_COLOR)
        pygame.draw.circle(canvas, DROP_FILL_COLOR, DROP_CENTER, DROP_RADIUS)
        pygame.draw.circle(canvas, DROP_OUTLINE_COLOR, DROP_CENTER, DROP_RADIUS, 2)
        canvas.blit(primary_canvas, (0, 0), special_flags=pygame.BLEND_ADD)
        canvas.blit(secondary_canvas, (0, 0), special_flags=pygame.BLEND_ADD)
        buttons = draw_buttons(canvas, font, primary_visible, secondary_visible)

        # Rita den skalade canvasen centrerad
        screen.fill(BACKGROUND_COLOR) # Rensa kanter
        scaled_surf = pygame.transform.scale(canvas, (new_w, new_h))
        screen.blit(scaled_surf, (offset_x, offset_y))
        
        pygame.display.flip()
        clock.tick(60)
    return

if __name__ == "__main__":
    main()