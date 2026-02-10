import pygame
import math
import sys

# --- Constants ---
# Logisk upplösning (simuleringen sker alltid i denna storlek)
WIDTH, HEIGHT = 1200, 800
BACKGROUND_COLOR = (5, 5, 5) # Very dark background

# Drop settings
DROP_CENTER = (WIDTH // 2, 200)
DROP_RADIUS = 23 # Ökad med ca 50% (från 15)

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BUTTON_COLOR = (50, 50, 80)
BUTTON_ACTIVE_COLOR = (80, 100, 80)
BUTTON_CLEAR_COLOR = (100, 50, 50) # Reddish for clear

# Drop Colors (Samma som i tidigare fil)
DROP_FILL_COLOR = (20, 20, 60)
DROP_OUTLINE_COLOR = (200, 200, 220)

# Rainbow Colors & Refractive Indices
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
    """
    Calculates the ray path for a given x_offset (signed).
    """
    points = []
    
    # 1. Start point (Bottom of screen)
    start_x = DROP_CENTER[0] + x_offset
    start_y = HEIGHT
    points.append((start_x, start_y))

    # 2. Entry point
    if abs(x_offset) > DROP_RADIUS:
        return points # Misses drop
    
    dy_entry = math.sqrt(DROP_RADIUS**2 - x_offset**2)
    entry_x = start_x
    entry_y = DROP_CENTER[1] + dy_entry
    points.append((entry_x, entry_y))

    # Snell's Law
    try:
        alpha = math.asin(x_offset / DROP_RADIUS)
    except ValueError:
        return points

    sin_beta = (1.0003 / n_color) * math.sin(alpha)
    if abs(sin_beta) > 1:
        return points 
    
    beta = math.asin(sin_beta)

    # Polar angle of entry
    theta_current = math.atan2(dy_entry, x_offset)
    
    # Rotation step logic
    rotation_step = -(math.pi - 2 * beta)

    # 3. Internal Reflections
    for _ in range(num_reflections):
        theta_current += rotation_step
        ref_x = DROP_CENTER[0] + DROP_RADIUS * math.cos(theta_current)
        ref_y = DROP_CENTER[1] + DROP_RADIUS * math.sin(theta_current)
        points.append((ref_x, ref_y))

    # 4. Exit
    theta_current += rotation_step
    exit_x = DROP_CENTER[0] + DROP_RADIUS * math.cos(theta_current)
    exit_y = DROP_CENTER[1] + DROP_RADIUS * math.sin(theta_current)
    points.append((exit_x, exit_y))
    
    # 5. Outgoing Ray
    final_ray_angle = theta_current - alpha
    
    end_x = exit_x + 3000 * math.cos(final_ray_angle) 
    end_y = exit_y + 3000 * math.sin(final_ray_angle)
    points.append((end_x, end_y))
    
    return points

def draw_buttons(surface, font, primary_visible, secondary_visible):
    """Draws toggle buttons on the given surface and returns their rects."""
    buttons = []
    start_x = 20
    start_y = 20
    
    # Primary Toggle
    p_text = f"Single: {'CLEAR' if primary_visible else 'START'}"
    surf = font.render(p_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    
    color = BUTTON_CLEAR_COLOR if primary_visible else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, GRAY, rect, 2, border_radius=5)
    surface.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "toggle_primary"})
    
    start_x += rect.width + 20
    
    # Secondary Toggle
    s_text = f"Double: {'CLEAR' if secondary_visible else 'START'}"
    surf = font.render(s_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    
    color = BUTTON_CLEAR_COLOR if secondary_visible else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, GRAY, rect, 2, border_radius=5)
    surface.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "toggle_secondary"})
    
    return buttons

def main():
    pygame.init()
    # Initiera fönstret som skalbart
    current_w, current_h = WIDTH, HEIGHT
    screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
    pygame.display.set_caption("Rainbow Shower Animation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    
    # Intern canvas för rendering (behåller fast upplösning för logik)
    canvas = pygame.Surface((WIDTH, HEIGHT))
    
    # Persistent layers for accumulation (alltid i logisk storlek)
    primary_canvas = pygame.Surface((WIDTH, HEIGHT))
    primary_canvas.fill((0, 0, 0))
    
    secondary_canvas = pygame.Surface((WIDTH, HEIGHT))
    secondary_canvas.fill((0, 0, 0))
    
    # Animation State
    animating_primary = False
    primary_visible = False 
    p_current_offset = -DROP_RADIUS * 0.99 
    
    animating_secondary = False
    secondary_visible = False
    s_current_offset = -DROP_RADIUS * 0.99 
    
    # Settings
    step_size = 0.1 
    rays_to_draw_per_frame = 1 

    # Initial button list
    buttons = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                current_w, current_h = event.w, event.h
                # Uppdatera inte display mode här om det redan är rätt, 
                # men vi behöver current_w/h för skalning vid utritning.
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Skala muspositionen till logiska koordinater
                    mx, my = event.pos
                    scale_x = WIDTH / current_w
                    scale_y = HEIGHT / current_h
                    logical_pos = (mx * scale_x, my * scale_y)
                    
                    for btn in buttons:
                        if btn["rect"].collidepoint(logical_pos):
                            if btn["action"] == "toggle_primary":
                                if primary_visible:
                                    # CLEAR
                                    animating_primary = False
                                    primary_visible = False
                                    primary_canvas.fill((0,0,0))
                                else:
                                    # START
                                    animating_primary = True
                                    primary_visible = True
                                    p_current_offset = -DROP_RADIUS * 0.99
                                    primary_canvas.fill((0,0,0))
                                
                            elif btn["action"] == "toggle_secondary":
                                if secondary_visible:
                                    # CLEAR
                                    animating_secondary = False
                                    secondary_visible = False
                                    secondary_canvas.fill((0,0,0))
                                else:
                                    # START
                                    animating_secondary = True
                                    secondary_visible = True
                                    s_current_offset = -DROP_RADIUS * 0.99
                                    secondary_canvas.fill((0,0,0))

        # --- Update Animation Primary ---
        if animating_primary:
            for _ in range(rays_to_draw_per_frame):
                if p_current_offset > DROP_RADIUS * 0.99:
                    animating_primary = False
                    break
                
                offset = p_current_offset
                
                # Draw rays for this step
                for data in RAINBOW_DATA:
                    col = (*data["rgb"], 50) # Additive intensity
                    path = calculate_ray_path_from_bottom(offset, data["n"], 1)
                    if len(path) >= 2:
                        temp = pygame.Surface((WIDTH, HEIGHT))
                        pygame.draw.lines(temp, col, False, path, 1)
                        primary_canvas.blit(temp, (0,0), special_flags=pygame.BLEND_ADD)
                
                p_current_offset += step_size

        # --- Update Animation Secondary ---
        if animating_secondary:
            for _ in range(rays_to_draw_per_frame):
                if s_current_offset > DROP_RADIUS * 0.99:
                    animating_secondary = False
                    break
                
                offset = s_current_offset
                
                for data in RAINBOW_DATA:
                    col = (*data["rgb"], 35)
                    path = calculate_ray_path_from_bottom(offset, data["n"], 2)
                    if len(path) >= 2:
                        temp = pygame.Surface((WIDTH, HEIGHT))
                        pygame.draw.lines(temp, col, False, path, 1)
                        secondary_canvas.blit(temp, (0,0), special_flags=pygame.BLEND_ADD)
                
                s_current_offset += step_size

        # --- Draw to internal canvas ---
        canvas.fill(BACKGROUND_COLOR)

        # Draw Drop (Fylld + Kant)
        pygame.draw.circle(canvas, DROP_FILL_COLOR, DROP_CENTER, DROP_RADIUS)
        pygame.draw.circle(canvas, DROP_OUTLINE_COLOR, DROP_CENTER, DROP_RADIUS, 2)
        
        # Blit accumulated canvases with ADD blending
        canvas.blit(primary_canvas, (0, 0), special_flags=pygame.BLEND_ADD)
        canvas.blit(secondary_canvas, (0, 0), special_flags=pygame.BLEND_ADD)
            
        # Draw UI
        buttons = draw_buttons(canvas, font, primary_visible, secondary_visible)

        # Skala upp canvasen och rita på skärmen
        scaled_surf = pygame.transform.scale(canvas, (current_w, current_h))
        screen.blit(scaled_surf, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    return

if __name__ == "__main__":
    main()