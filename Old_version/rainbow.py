import pygame
import math
import random
import sys
import os

# --- Constants ---
# Intern upplösning (simuleringen sker alltid i denna storlek)
INTERNAL_WIDTH, INTERNAL_HEIGHT = 1200, 800
FOV_DEGREES = 70.0   
SUN_ELEVATION = 40.0 
GLOBAL_INTENSITY = 2.5
# Offset för den manuella markören så man ser vad man gör
MANUAL_CURSOR_OFFSET = (-10, -10) 

def gaussian(x, mu, sigma):
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)

def get_rainbow_color(angle_deg):
    """
    Returns (r, g, b) intensity.
    Tuned for realistic, subtle appearance with smoother gradients.
    """
    r, g, b = 0.0, 0.0, 0.0
    
    # 1. Retroreflection (Heiligenschein)
    retro_peak = 0.8 * math.exp(-0.5 * (angle_deg / 0.8) ** 2)
    r += retro_peak
    g += retro_peak
    b += retro_peak

    # 2. Geometric Optics "Glow" (Inside Primary Bow)
    if angle_deg < 42.0:
        glow = 0.20 + 0.08 * math.exp((angle_deg - 42.0) * 0.15)
        r += glow
        g += glow
        b += glow
    
    # 3. Primary Rainbow (~40.8 - 42.5 deg)
    if 38.0 < angle_deg < 45.0:
        intensity_prim = 0.6
        b += intensity_prim * gaussian(angle_deg, 40.8, 1.4) 
        g += intensity_prim * gaussian(angle_deg, 41.6, 1.3)
        r += intensity_prim * gaussian(angle_deg, 42.3, 1.3)

    # 4. Light outside Alexander's Dark Band (> 50.0 deg)
    if angle_deg > 50.0:
        outer_glow = 0.05 
        r += outer_glow
        g += outer_glow
        b += outer_glow

    # 5. Secondary Rainbow (~50.5 - 53.5 deg)
    if 48.0 < angle_deg < 56.0:
        intensity_sec = 0.22
        r += intensity_sec * gaussian(angle_deg, 50.6, 1.6)
        g += intensity_sec * gaussian(angle_deg, 52.0, 1.6)
        b += intensity_sec * gaussian(angle_deg, 53.4, 1.6)

    return r, g, b

def create_fallback_landscape():
    """Generates a simple background if landscape.jpg is missing."""
    surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    # Sky Gradient
    for y in range(INTERNAL_HEIGHT//2):
        val = int(255 * (y / (INTERNAL_HEIGHT//2)))
        col = (50, 100, 150 + val//3)
        pygame.draw.line(surf, col, (0, y), (INTERNAL_WIDTH, y))
    
    # Ground
    pygame.draw.rect(surf, (20, 40, 20), (0, INTERNAL_HEIGHT//2, INTERNAL_WIDTH, INTERNAL_HEIGHT//2))
    
    font = pygame.font.SysFont("Arial", 30)
    txt = font.render("Ingen 'landscape.jpg' hittades.", True, (200, 200, 200))
    surf.blit(txt, (20, 20))
    return surf

def calculate_pixel_color(px, py, asp_x, asp_y, view_dist, boost_intensity=False):
    """
    Helper to calculate RGB color for a specific pixel coordinate.
    boost_intensity=True gör färgen mycket starkare för förhandsvisning.
    """
    dx = px - asp_x
    dy = py - asp_y
    r_px = math.sqrt(dx*dx + dy*dy)
    angle = math.degrees(math.atan2(r_px, view_dist))
    
    if angle < 65.0:
        rf, gf, bf = get_rainbow_color(angle)
        if rf > 0.001 or gf > 0.001 or bf > 0.001:
            # Bas-ljusstyrka för BLEND_MAX
            brightness = 150
            
            # Om vi boostar, multiplicera med en faktor (t.ex. 3x)
            intensity_multiplier = GLOBAL_INTENSITY
            if boost_intensity:
                intensity_multiplier *= 3.0
            
            r = min(255, int(rf * brightness * intensity_multiplier))
            g = min(255, int(gf * brightness * intensity_multiplier))
            b = min(255, int(bf * brightness * intensity_multiplier))
            return (r, g, b)
            
    return (0, 0, 0)

def main():
    pygame.init()
    # Initiera fönstret som skalbart
    current_w, current_h = INTERNAL_WIDTH, INTERNAL_HEIGHT
    screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
    pygame.display.set_caption("Regnbågssimulering: Monte Carlo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    # Intern canvas för rendering
    canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

    # 1. Load Background
    try:
        if os.path.exists("landscape.jpg"):
            bg_image = pygame.image.load("landscape.jpg")
            bg_image = pygame.transform.scale(bg_image, (INTERNAL_WIDTH, INTERNAL_HEIGHT))
        else:
            raise FileNotFoundError
    except:
        bg_image = create_fallback_landscape()

    # 2. Setup Physics Geometry
    fov_rad = math.radians(FOV_DEGREES)
    view_dist = (INTERNAL_WIDTH / 2) / math.tan(fov_rad / 2)
    
    asp_angle_rad = math.radians(SUN_ELEVATION)
    
    # Anti-Solar Point on screen
    asp_pixel_y = (INTERNAL_HEIGHT / 2) + math.tan(asp_angle_rad) * view_dist
    asp_pixel_x = INTERNAL_WIDTH / 2

    # 3. Additive Layer
    rainbow_layer = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    rainbow_layer.fill((0, 0, 0))
    
    # UI Elements
    start_btn = pygame.Rect(10, 50, 120, 35)
    clear_btn = pygame.Rect(140, 50, 100, 35)
    
    # State
    running = True
    simulating = False # Starts paused
    manual_dragging = False
    manual_pos = (0, 0) # Logisk position (interna koordinater)
    
    points_per_frame = 2.0
    acceleration = 1.02 
    max_points = 20000 
    total_points = 0
    
    print("Startar applikation...")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.VIDEORESIZE:
                current_w, current_h = event.w, event.h
                screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click
                    # Skala musen till interna koordinater
                    mx, my = event.pos
                    scale_x = INTERNAL_WIDTH / current_w
                    scale_y = INTERNAL_HEIGHT / current_h
                    logical_pos = (mx * scale_x, my * scale_y)

                    if start_btn.collidepoint(logical_pos):
                        # Toggle Simulation
                        simulating = not simulating
                    elif clear_btn.collidepoint(logical_pos):
                        # Clear
                        rainbow_layer.fill((0,0,0))
                        total_points = 0
                        points_per_frame = 2.0 # Återställ hastighet
                    else:
                        # Start Manual Placement
                        manual_dragging = True
                        manual_pos = logical_pos
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and manual_dragging:
                    # Använd manual_pos som redan är i logiska koordinater från MOUSEMOTION
                    target_pos = (manual_pos[0] + MANUAL_CURSOR_OFFSET[0], manual_pos[1] + MANUAL_CURSOR_OFFSET[1])
                    
                    # "Stämpla" droppen med KORREKT (icke-boostad) intensitet
                    col = calculate_pixel_color(target_pos[0], target_pos[1], asp_pixel_x, asp_pixel_y, view_dist, boost_intensity=False)
                    
                    if col != (0,0,0):
                        radius = 6 
                        temp_stamp = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
                        temp_stamp.fill((0,0,0,0))
                        pygame.draw.circle(temp_stamp, col, target_pos, radius)
                        rainbow_layer.blit(temp_stamp, (0,0), special_flags=pygame.BLEND_MAX)
                        total_points += 1 
                    
                    manual_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                # Skala musen
                mx, my = event.pos
                scale_x = INTERNAL_WIDTH / current_w
                scale_y = INTERNAL_HEIGHT / current_h
                manual_pos = (mx * scale_x, my * scale_y)

        # --- Automatic Random Drops (Simulation) ---
        if simulating:
            count = int(points_per_frame)
            frame_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
            frame_surface.fill((0,0,0))
            
            if count > 0:
                pixels = pygame.PixelArray(frame_surface)
                for _ in range(count):
                    px = int(random.uniform(0, INTERNAL_WIDTH))
                    py = int(random.uniform(0, INTERNAL_HEIGHT))
                    
                    # Automatisk simulering använder alltid korrekt intensitet (boost=False)
                    col = calculate_pixel_color(px, py, asp_pixel_x, asp_pixel_y, view_dist, boost_intensity=False)
                    if col != (0,0,0):
                        pixels[px, py] = col
                
                pixels.close()
                rainbow_layer.blit(frame_surface, (0,0), special_flags=pygame.BLEND_MAX)

            # Acceleration
            points_per_frame *= acceleration
            if points_per_frame > max_points: points_per_frame = max_points
            total_points += count

        # --- Drawing to Internal Canvas ---
        canvas.blit(bg_image, (0, 0))
        canvas.blit(rainbow_layer, (0, 0), special_flags=pygame.BLEND_ADD)

        # Draw Manual Droplet Cursor (Preview)
        if manual_dragging:
            target_pos = (manual_pos[0] + MANUAL_CURSOR_OFFSET[0], manual_pos[1] + MANUAL_CURSOR_OFFSET[1])
            
            # Använd BOOSTAD intensitet för förhandsvisningen
            col = calculate_pixel_color(target_pos[0], target_pos[1], asp_pixel_x, asp_pixel_y, view_dist, boost_intensity=True)
            
            # Rita glöd och kontur
            pygame.draw.circle(canvas, col, target_pos, 8) 
            pygame.draw.circle(canvas, (255, 255, 255), target_pos, 9, 1)
            pygame.draw.line(canvas, (200, 200, 200), manual_pos, target_pos, 1)

        # UI
        status = f"Droppar: {total_points:,} | Hastighet: {int(points_per_frame) if simulating else 0}/bild"
        txt = font.render(status, True, (255, 255, 255))
        canvas.blit(txt, (15, 15))
        
        # Helper for drawing buttons
        # Get mouse pos in logical coords for hover effect
        raw_mx, raw_my = pygame.mouse.get_pos()
        scale_x = INTERNAL_WIDTH / current_w
        scale_y = INTERNAL_HEIGHT / current_h
        log_mx, log_my = raw_mx * scale_x, raw_my * scale_y

        # Start/Stop Button
        btn_hover = start_btn.collidepoint((log_mx, log_my))
        if simulating:
            base_col = (100, 150, 100) if btn_hover else (60, 100, 60)
            text_str = "Stoppa Regn"
        else:
            base_col = (100, 100, 150) if btn_hover else (60, 60, 100)
            text_str = "Starta Regn"
            
        pygame.draw.rect(canvas, base_col, start_btn, border_radius=5)
        pygame.draw.rect(canvas, (200, 200, 200), start_btn, 1, border_radius=5)
        btn_txt = font.render(text_str, True, (255, 255, 255))
        canvas.blit(btn_txt, (start_btn.centerx - btn_txt.get_width()//2, start_btn.centery - btn_txt.get_height()//2))

        # Clear Button
        clear_hover = clear_btn.collidepoint((log_mx, log_my))
        clear_col = (150, 100, 100) if clear_hover else (100, 60, 60)
        pygame.draw.rect(canvas, clear_col, clear_btn, border_radius=5)
        pygame.draw.rect(canvas, (200, 200, 200), clear_btn, 1, border_radius=5)
        clear_txt = font.render("Rensa", True, (255, 255, 255))
        canvas.blit(clear_txt, (clear_btn.centerx - clear_txt.get_width()//2, clear_btn.centery - clear_txt.get_height()//2))

        # Instructions
        if not simulating and total_points == 0:
            inst = font.render("Klicka & Dra för att placera droppar manuellt.", True, (200, 200, 200))
            canvas.blit(inst, (250, 60))

        # Scale and draw to screen
        scaled_surf = pygame.transform.scale(canvas, (current_w, current_h))
        screen.blit(scaled_surf, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    return

if __name__ == "__main__":
    main()