import pygame
import math
import sys

# --- Constants ---
WIDTH, HEIGHT = 1200, 800
BACKGROUND_COLOR = (20, 20, 20)
UI_WIDTH = 250

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
UI_TEXT_COLOR = (200, 200, 200)
BUTTON_COLOR = (50, 50, 80)
BUTTON_HOVER_COLOR = (70, 70, 100)
BUTTON_ACTIVE_COLOR = (80, 100, 80)

# Drop Colors
DROP_FILL_COLOR = (20, 20, 60)   # Något ljusare blå
DROP_OUTLINE_COLOR = (200, 200, 220) # Tydligare vit kant

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

class SimulationState:
    def __init__(self):
        # Initialize with all beams OFF
        self.visible_flags = [False] * 7
        self.focused_index = 0
        
        # Independent impact values for Primary (Left) and Secondary (Right)
        self.impact_primary = [100.0] * 7 
        self.impact_secondary = [100.0] * 7
        
        self.is_dragging = False
        
        # Toggles
        self.show_primary = True
        self.show_secondary = False

def get_layout(current_w, current_h):
    ui_x = current_w - UI_WIDTH
    drop_center = (ui_x // 2, current_h // 2)
    
    # Scale droplet based on window size (removed fixed 150px limit)
    # Ensure it fits both width (leaving space for UI) and height
    max_radius_w = (ui_x - 50) // 6
    max_radius_h = current_h // 7.5
    drop_radius = int(min(max_radius_w, max_radius_h))
    
    return ui_x, drop_center, drop_radius

def calculate_ray_path_from_bottom(x_offset, n_color, drop_center, drop_radius, screen_height, num_reflections):
    """
    Calculates the ray path.
    """
    points = []
    
    # 1. Start point
    start_x = drop_center[0] + x_offset
    start_y = screen_height
    points.append((start_x, start_y))

    # 2. Entry point
    if abs(x_offset) > drop_radius:
        points.append((start_x, 0))
        return points, None 
    
    dy_entry = math.sqrt(drop_radius**2 - x_offset**2)
    entry_x = start_x
    entry_y = drop_center[1] + dy_entry
    points.append((entry_x, entry_y))

    # Snell's Law
    try:
        alpha = math.asin(x_offset / drop_radius)
    except ValueError:
        return points, None

    sin_beta = (1.0003 / n_color) * math.sin(alpha)
    if abs(sin_beta) > 1:
        return points, None 
    
    beta = math.asin(sin_beta)

    # Polar coordinate angle of entry
    theta_current = math.atan2(dy_entry, x_offset)
    
    # Rotation step logic
    rotation_step = -(math.pi - 2 * beta)

    # 3. Internal Reflections
    for _ in range(num_reflections):
        theta_current += rotation_step
        ref_x = drop_center[0] + drop_radius * math.cos(theta_current)
        ref_y = drop_center[1] + drop_radius * math.sin(theta_current)
        points.append((ref_x, ref_y))

    # 4. Exit
    theta_current += rotation_step
    exit_x = drop_center[0] + drop_radius * math.cos(theta_current)
    exit_y = drop_center[1] + drop_radius * math.sin(theta_current)
    points.append((exit_x, exit_y))
    
    # 5. Outgoing Ray
    final_ray_angle = theta_current - alpha
    
    end_x = exit_x + 2000 * math.cos(final_ray_angle)
    end_y = exit_y + 2000 * math.sin(final_ray_angle)
    points.append((end_x, end_y))
    
    # Calculate Deviation
    alpha_deg = math.degrees(abs(alpha))
    beta_deg = math.degrees(abs(beta))
    
    if num_reflections == 1:
        calc_deviation = 4 * beta_deg - 2 * alpha_deg
    else:
        calc_deviation = 180 + 2 * alpha_deg - 6 * beta_deg
        
    return points, abs(calc_deviation)

def draw_ui_right_panel(screen, state, font, ui_x_start, screen_height):
    pygame.draw.rect(screen, (40, 40, 40), (ui_x_start, 0, UI_WIDTH, screen_height))
    pygame.draw.line(screen, GRAY, (ui_x_start, 0), (ui_x_start, screen_height), 2)
    
    title = font.render("Colors", True, WHITE)
    screen.blit(title, (ui_x_start + 20, 20))
    
    start_y = 60
    spacing = 50
    
    l1 = font.render("Vis", True, GRAY)
    l2 = font.render("Control", True, GRAY)
    screen.blit(l1, (ui_x_start + 10, start_y - 20))
    screen.blit(l2, (ui_x_start + 60, start_y - 20))

    for i, data in enumerate(RAINBOW_DATA):
        y_pos = start_y + i * spacing
        
        # Checkbox
        checkbox_rect = pygame.Rect(ui_x_start + 10, y_pos, 20, 20)
        pygame.draw.rect(screen, GRAY, checkbox_rect, 2)
        if state.visible_flags[i]:
            pygame.draw.rect(screen, data["rgb"], (checkbox_rect.x+4, checkbox_rect.y+4, 12, 12))
            
        # Radio Button
        radio_center = (ui_x_start + 80, y_pos + 10)
        pygame.draw.circle(screen, GRAY, radio_center, 10, 2)
        if state.focused_index == i:
            pygame.draw.circle(screen, WHITE, radio_center, 6)
            
        color_name = font.render(data["name"], True, data["rgb"])
        screen.blit(color_name, (ui_x_start + 110, y_pos))

    inst_y = screen_height - 120
    lines = ["Drag Left side", "for Primary.", "Drag Right side", "for Secondary."]
    for idx, line in enumerate(lines):
        inst_surf = font.render(line, True, GRAY)
        screen.blit(inst_surf, (ui_x_start + 10, inst_y + (idx*20)))

def draw_top_controls(screen, state, font):
    buttons = []
    start_x = 20
    start_y = 20
    
    # Primary Toggle
    p_text = f"Primary (Single): {'ON' if state.show_primary else 'OFF'}"
    surf = font.render(p_text, True, WHITE if state.show_primary else GRAY)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    
    color = BUTTON_ACTIVE_COLOR if state.show_primary else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=5)
    pygame.draw.rect(screen, GRAY, rect, 2, border_radius=5)
    screen.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "toggle_primary"})
    
    start_x += rect.width + 20
    
    # Secondary Toggle
    s_text = f"Secondary (Double): {'ON' if state.show_secondary else 'OFF'}"
    surf = font.render(s_text, True, WHITE if state.show_secondary else GRAY)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    
    color = BUTTON_ACTIVE_COLOR if state.show_secondary else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=5)
    pygame.draw.rect(screen, GRAY, rect, 2, border_radius=5)
    screen.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "toggle_secondary"})
    
    start_x += rect.width + 20
    
    # Set Optimal Angles
    opt_text = "Set Optimal Angles"
    surf = font.render(opt_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    
    pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=5)
    pygame.draw.rect(screen, GRAY, rect, 2, border_radius=5)
    screen.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "set_optimal"})
    
    return buttons

def handle_click(pos, state, ui_x_start, top_buttons, drop_radius):
    x, y = pos
    
    for btn in top_buttons:
        if btn["rect"].collidepoint(pos):
            if btn["action"] == "toggle_primary":
                state.show_primary = not state.show_primary
            elif btn["action"] == "toggle_secondary":
                state.show_secondary = not state.show_secondary
            elif btn["action"] == "set_optimal":
                for i, data in enumerate(RAINBOW_DATA):
                    n = data["n"]
                    if 4 - n**2 > 0:
                        b_primary = drop_radius * math.sqrt((4 - n**2) / 3)
                        state.impact_primary[i] = b_primary
                    if 9 - n**2 > 0:
                        b_secondary = drop_radius * math.sqrt((9 - n**2) / 8)
                        state.impact_secondary[i] = b_secondary
                state.show_primary = True
                state.show_secondary = True
            return True

    if x >= ui_x_start:
        start_y = 60
        spacing = 50
        for i in range(len(RAINBOW_DATA)):
            y_pos = start_y + i * spacing
            if (ui_x_start + 10 <= x <= ui_x_start + 30) and (y_pos <= y <= y_pos + 20):
                state.visible_flags[i] = not state.visible_flags[i]
                state.focused_index = i
            if (ui_x_start + 60 <= x <= ui_x_start + 100) and (y_pos <= y <= y_pos + 20):
                state.focused_index = i
        return True
        
    return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Physics Simulation: The Rainbow")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    
    state = SimulationState()
    current_w, current_h = WIDTH, HEIGHT
    buttons = []

    running = True
    while running:
        ui_x_start, drop_center, drop_radius = get_layout(current_w, current_h)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                current_w, current_h = event.w, event.h
                screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    ui_hit = handle_click(event.pos, state, ui_x_start, buttons, drop_radius)
                    if not ui_hit:
                        state.is_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                state.is_dragging = False
        
        if state.is_dragging:
            mx, my = pygame.mouse.get_pos()
            if mx < ui_x_start:
                dx = mx - drop_center[0]
                raw_dist = abs(dx)
                limit = drop_radius - 2
                if raw_dist > limit: raw_dist = limit
                if raw_dist < 5: raw_dist = 5
                
                if dx < 0:
                    state.impact_primary[state.focused_index] = raw_dist
                else:
                    state.impact_secondary[state.focused_index] = raw_dist

        screen.fill(BACKGROUND_COLOR)
        
        # Draw Droplet (Filled Dark Blue)
        pygame.draw.circle(screen, DROP_FILL_COLOR, drop_center, drop_radius)
        # Draw Droplet Outline (Subtle)
        pygame.draw.circle(screen, DROP_OUTLINE_COLOR, drop_center, drop_radius, 2)
        
        # Guide Lines
        pygame.draw.line(screen, (50, 50, 50), (drop_center[0], 0), (drop_center[0], current_h), 1)
        pygame.draw.line(screen, (50, 50, 50), (0, drop_center[1]), (ui_x_start, drop_center[1]), 1)
        
        focused_deviation_p = 0.0
        focused_deviation_s = 0.0
        
        # --- ADDITIVE DRAWING LOGIC ---
        # 1. Create a black surface for rays
        ray_layer = pygame.Surface((current_w, current_h))
        ray_layer.fill((0, 0, 0))
        
        # 2. Draw rays onto ray_layer using additive blending logic
        for i, data in enumerate(RAINBOW_DATA):
            if state.visible_flags[i]:
                width = 2
                is_focused = (i == state.focused_index)
                if is_focused: width = 4
                
                # Scale color down so overlap sums to white (additive)
                # But keep focused ray bright enough to see
                intensity = 1.0 if is_focused else 0.7
                col = tuple(min(255, int(c * intensity)) for c in data["rgb"])
                
                temp_surf = pygame.Surface((current_w, current_h))
                temp_surf.fill((0,0,0))
                
                # Primary
                if state.show_primary:
                    impact_p = state.impact_primary[i]
                    path_p, dev_p = calculate_ray_path_from_bottom(
                        -impact_p, data["n"], drop_center, drop_radius, current_h, 1
                    )
                    if path_p:
                        pygame.draw.line(temp_surf, col, path_p[0], path_p[1], width)
                        pygame.draw.lines(temp_surf, col, False, path_p[1:], width)
                        if is_focused: focused_deviation_p = dev_p
                        
                # Secondary
                if state.show_secondary:
                    impact_s = state.impact_secondary[i]
                    path_s, dev_s = calculate_ray_path_from_bottom(
                        impact_s, data["n"], drop_center, drop_radius, current_h, 2
                    )
                    if path_s:
                        pygame.draw.line(temp_surf, col, path_s[0], path_s[1], width)
                        pygame.draw.lines(temp_surf, col, False, path_s[1:], width)
                        if is_focused: focused_deviation_s = dev_s
                
                # Add this color's lines to the main ray layer
                ray_layer.blit(temp_surf, (0,0), special_flags=pygame.BLEND_ADD)

        # 3. Blit the completed ray layer onto the main screen
        screen.blit(ray_layer, (0,0), special_flags=pygame.BLEND_ADD)

        # Draw UI
        buttons = draw_top_controls(screen, state, font)
        draw_ui_right_panel(screen, state, font, ui_x_start, current_h)
        
        # Info Text
        if focused_deviation_p or focused_deviation_s:
            big_font = pygame.font.SysFont("Arial", 20, bold=True)
            txt_lines = [f"Color: {RAINBOW_DATA[state.focused_index]['name']}"]
            if state.show_primary:
                txt_lines.append(f"Primary Angle: {focused_deviation_p:.1f}°")
            if state.show_secondary:
                txt_lines.append(f"Secondary Angle: {focused_deviation_s:.1f}°")
                
            for idx, txt in enumerate(txt_lines):
                surf = big_font.render(txt, True, WHITE)
                screen.blit(surf, (drop_center[0] + drop_radius + 20, drop_center[1] - drop_radius - 60 + idx*25))

        pygame.display.flip()
        clock.tick(60)

    return

if __name__ == "__main__":
    main()